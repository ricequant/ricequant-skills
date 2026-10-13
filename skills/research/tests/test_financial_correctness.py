"""Financial regressions using synthetic fixtures, no live market/API access."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import re
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[2]
CUTOFF = date(2024, 4, 10)
STOCK = 'SYNTHETIC'
MODULES = {}
for name in ('idea-generation', 'sector-overview', 'earnings-preview',
             'earnings-analysis', 'initiating-coverage', 'thesis-tracker'):
    filename = 'build_screening_snapshot.py' if name == 'idea-generation' else 'generate_report.py'
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT/'research'/name/'scripts'/filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    MODULES[name] = module


def financial(quarter, disclosed, profit, revenue=130):
    return dict(order_book_id=STOCK, quarter=quarter, info_date=disclosed,
                net_profit=profit, revenue=revenue, total_assets=1000, total_liabilities=200)


def factors():
    return [dict(order_book_id=STOCK, date=CUTOFF.isoformat(),
                 return_on_equity_weighted_average=20)]


def idea_rows(latest, history=None):
    return MODULES['idea-generation'].build_universe_rows(
        [STOCK], [], latest, latest if history is None else history,
        factors(), [], [], [], CUTOFF)


class FinancialCorrectnessTests(unittest.TestCase):
    def test_cagr_requires_positive_original_endpoints(self):
        mod = MODULES['initiating-coverage']
        for values in (
            [(2020, -100), (2024, -200)],
            [(2020, -100), (2024, 100)],
            [(2020, 100), (2024, -100)],
            [(2020, 0), (2021, 100), (2024, 200)],
            [(2020, 100), (2023, 200), (2024, 0)],
            [(2020, None), (2021, 100), (2024, 200)],
            [(2020, 100), (2023, 200), (2024, None)],
            [], [(2020, 100)], [(2020, 100), (2020, 200)],
        ):
            with self.subTest(values=values):
                self.assertIsNone(mod.cagr(values))

    def test_cagr_positive_endpoints_preserve_actual_year_span(self):
        mod = MODULES['initiating-coverage']
        for values, expected in (
            ([(2020, 100), (2024, 200)], (2 ** 0.25 - 1) * 100),
            ([(2020, 200), (2024, 100)], (0.5 ** 0.25 - 1) * 100),
            ([(2020, 100), (2024, 100)], 0),
            ([(2020, 100), (2022, None), (2024, 200)], (2 ** 0.25 - 1) * 100),
            ([(2020, 100), (2022, -50), (2024, 200)], (2 ** 0.25 - 1) * 100),
        ):
            with self.subTest(values=values):
                self.assertAlmostEqual(mod.cagr(values), expected)

    def test_coverage_cli_cagr_display(self):
        mod = MODULES['initiating-coverage']
        peers = [STOCK, 'PEER_ONE', 'PEER_TWO']
        peer_records = [dict(financial('2024q4', '2025-03-20', 100e8), order_book_id=peer)
                        for peer in peers]
        prices = [dict(order_book_id=STOCK, date=(date(2024, 8, 1) + timedelta(days=i)).isoformat(),
                       close=100 + i / 10) for i in range(120)]
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            inputs = {
                'price_history.json': prices,
                'consensus.json': [dict(order_book_id=STOCK, date='2025-03-25',
                                        report_year_t=2025, comp_con_net_profit_t=100e8)],
                'peer_pool.json': peers,
                'peer_latest_financials.json': peer_records,
            }
            for filename, rows in inputs.items():
                (folder / filename).write_text(json.dumps(rows))
            for start, end, expected in ((-100e8, -200e8, '不可计算'),
                                          (-100e8, 100e8, '不可计算'),
                                          (0, 100e8, '不可计算'),
                                          (100e8, 0, '不可计算'),
                                          (100e8, 146.41e8, '+10.0%')):
                with self.subTest(start=start, end=end):
                    rows = [financial('2020q4', '2021-03-20', start, 100e8),
                            financial('2022q4', '2023-03-20', 120e8, 110e8),
                            financial('2024q4', '2025-03-20', end, 146.41e8)]
                    (folder / 'historical_financials.json').write_text(json.dumps(rows))
                    output = folder / 'coverage.md'
                    subprocess.run([sys.executable, mod.__file__, '--stock', STOCK,
                        '--data-dir', directory, '--report-date', '2025-04-10',
                        '--output', str(output), '--no-render'], check=True, capture_output=True,
                        env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
                    report = output.read_text()
                    self.assertIn(f'净利润 CAGR 为 {expected}', report)
                    self.assertIn('收入 CAGR 为 +10.0%', report)
                    self.assertNotRegex(report, r'[+-]?\d+\.\d+[+-]\d+\.\d+j%')

    def test_profit_change_classification(self):
        for name, mod in MODULES.items():
            for current, base, expected in [(-50, -100, '减亏'), (-200, -100, '亏损扩大'),
                                             (50, -100, '扭亏'), (-50, 100, '转亏'),
                                             (100, 100, '利润持平'), (0, -100, '盈亏平衡'),
                                             (50, 0, '同期基数为零'), (None, 100, '无数据')]:
                with self.subTest(skill=name, current=current, base=base):
                    self.assertEqual(mod.profit_change_type(current, base), expected)

    def test_collection_workflow_sends_historical_query_date(self):
        skill=(ROOT/'research/idea-generation/SKILL.md').read_text()
        snippet=re.search(r'python3 - "\$DATA_DIR" "\$REPORT_DATE" "\$START_QUARTER" "\$END_QUARTER" <<\'PY\'\n(.*?)\nPY',
                          skill, re.DOTALL).group(1)
        calls=[]
        def fake_cli(command, **kwargs):
            calls.append(command)
            return '[]'
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory)/'stock_pool.json').write_text(json.dumps([{'order_book_id':STOCK}]))
            with patch.object(sys,'argv',['-',directory,'2024-04-10','2022q1','2024q4']), \
                 patch.object(subprocess,'check_output',side_effect=fake_cli):
                exec(compile(snippet,'idea-generation collection workflow','exec'),{})
        financial_calls=[command for command in calls if command[:4]==['rqdata','stock','cn','financial']]
        self.assertEqual(len(financial_calls),1)
        payload=json.loads(financial_calls[0][financial_calls[0].index('--payload')+1])
        self.assertEqual(payload['date'],'2024-04-10')
        self.assertEqual(payload['statements'],'all')

    def test_signed_profit_growth_all_six_skills(self):
        for current, base, expected in [(-200,-100,-100),(-50,-100,50),
                                        (50,-100,150),(130,100,30),
                                        (-50,100,-150),(0,-100,100),
                                        (50,0,None),(None,100,None),(50,None,None)]:
            records=[financial('2022q4','2023-03-20',base,100),
                     financial('2023q4','2024-03-20',current)]
            values={
                'idea-generation': idea_rows(records)[0]['profit_yoy'],
                'sector-overview': MODULES['sector-overview'].build_sector_rows(
                    [STOCK],[],[],records,[],[],[],[],[],CUTOFF)[0][0]['profit_yoy'],
                'earnings-preview': MODULES['earnings-preview'].build_financial_trend(
                    records,STOCK,CUTOFF)[-1]['profit_yoy'],
                'thesis-tracker': MODULES['thesis-tracker'].metric_lookup(
                    records,None,None,None,{})['latest_net_profit_yoy_pct'],
            }
            for name in ('earnings-analysis','initiating-coverage'):
                values[name]=MODULES[name].safe_growth(current,base)
            for name,value in values.items():
                with self.subTest(skill=name,current=current,base=base):
                    if expected is None:
                        self.assertIsNone(value)
                    else:
                        self.assertAlmostEqual(value,expected)

    def test_growth_screen_direction(self):
        mod=MODULES['idea-generation']
        for profit,expected in [(-200,False),(-50,True),(50,True),(130,True)]:
            base=100 if profit==130 else -100
            records=[financial('2022q4','2023-03-20',base,100),
                     financial('2023q4','2024-03-20',profit)]
            self.assertEqual(bool(mod.screen_growth(idea_rows(records),10,15,20,15)),expected)

    def test_financial_cutoff_before_deduplication(self):
        records=[financial('2023q4','2024-03-20',100),
                 financial('2023q4','2024-04-10',120),
                 financial('2023q4','2024-04-20',999),
                 financial('2024q1','2024-04-25',777),
                 financial('2024q2',None,888),financial('2024q3','invalid',888)]
        for name,mod in MODULES.items():
            with self.subTest(skill=name):
                ids=[STOCK] if name in ('idea-generation','sector-overview','initiating-coverage') else STOCK
                selected=mod.dedupe_financial_records(records,ids,CUTOFF)
                self.assertEqual([(r['quarter'],r['net_profit']) for r in selected],[('2023q4',120)])

    def test_factor_cutoff(self):
        records=[dict(order_book_id=STOCK,date='2024-04-10',market_cap=100),
                 dict(order_book_id=STOCK,date='2024-04-20',market_cap=999)]
        for name in ('idea-generation','sector-overview'):
            self.assertEqual(MODULES[name].latest_factor_map(records,[STOCK],'market_cap',CUTOFF),{STOCK:100})

    def test_peer_cutoff(self):
        records=[financial('2023q4','2024-03-20',120),
                 financial('2023q4','2024-04-20',999),
                 financial('2024q1','2024-04-25',777),financial('2024q2',None,888)]
        peer=MODULES['earnings-preview'].build_peer_snapshot(records,[],CUTOFF)
        self.assertEqual([(r['quarter'],r['net_profit']) for r in peer['rows']],[('2023q4',120)])

    def test_yoy_matches_selected_quarter_across_files(self):
        latest=[financial('2023q4','2024-03-20',150)]
        history=[financial('2022q4','2023-03-20',100,100),
                 financial('2022q3','2022-10-20',10,100)]
        row=idea_rows(latest,history)[0]
        self.assertEqual(row['latest_quarter'],'2023q4')
        self.assertAlmostEqual(row['profit_yoy'],50)
        self.assertAlmostEqual(row['revenue_yoy'],30)

    def test_negative_anchor_forecast_and_scenarios(self):
        mod=MODULES['earnings-preview']
        trend=[dict(quarter='2023q1',net_profit=-100,revenue=100,profit_yoy=50,revenue_yoy=20)]
        forecast=mod.forecast_target_quarter(trend,'2024q1')
        self.assertAlmostEqual(forecast['predicted_profit'],-50)
        scenarios=mod.build_scenarios(forecast,{})
        profits=[row['profit'] for row in scenarios]
        self.assertGreater(profits[0],profits[1])
        self.assertGreater(profits[1],profits[2])
        self.assertAlmostEqual(profits[1],forecast['predicted_profit'])

    def test_original_cli_excludes_future_quarters_and_revisions(self):
        mod=MODULES['idea-generation']
        history=[financial('2022q4','2023-03-20',100,100),
                 financial('2023q4','2024-03-20',130),
                 financial('2023q4','2024-04-20',999),
                 financial('2024q1','2024-04-25',777)]
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            for filename,records in {'stock_pool.json':[dict(order_book_id=STOCK)],
                'financials_history.json':history,'latest_financials.json':history,'roe.json':factors()}.items():
                (folder/filename).write_text(json.dumps(records))
            snapshots=[]
            for cutoff in ('2024-04-10','2024-05-10'):
                output=folder/f'{cutoff}.json'
                subprocess.run([sys.executable,mod.__file__,'--strategy','all','--data-dir',directory,
                    '--report-date',cutoff,'--output',str(output)],check=True,capture_output=True,
                    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
                snapshots.append(json.loads(output.read_text()))
            early,late=snapshots
            self.assertEqual(early['universe']['latest_quarters'],[{'name':'2023q4','count':1}])
            candidate=early['strategies']['growth']['display_candidates'][0]
            self.assertEqual(candidate['net_profit'],130)
            self.assertAlmostEqual(candidate['profit_yoy'],30)
            self.assertEqual(late['universe']['latest_quarters'],[{'name':'2024q1','count':1}])


if __name__=='__main__':
    unittest.main()
