import os
import random
from datetime import datetime, timedelta


class GA4Client:
    """
    Клиент для работы с GA4.
    Если USE_MOCK=True, возвращает реалистичные тестовые данные.
    Если False, подключается к реальному GA4 API.
    """

    def __init__(self, property_id: str, use_mock: bool = True):
        self.property_id = property_id
        self.use_mock = use_mock

        if not use_mock:
            # Реальный клиент GA4
            from google.analytics.data_v1beta import BetaAnalyticsDataClient
            from google.analytics.data_v1beta.types import (
                RunReportRequest, DateRange, Metric, Dimension
            )
            self.client = BetaAnalyticsDataClient()
            self.RunReportRequest = RunReportRequest
            self.DateRange = DateRange
            self.Metric = Metric
            self.Dimension = Dimension

    def query(
        self,
        metrics: list[str],
        start_date: str,
        end_date: str,
        dimensions: list[str] = None
    ) -> dict:
        """
        Главный метод запроса данных.
        Возвращает словарь с результатами.
        """
        if self.use_mock:
            return self._mock_query(metrics, start_date, end_date, dimensions)
        else:
            return self._real_query(metrics, start_date, end_date, dimensions)

    def _mock_query(
        self,
        metrics: list[str],
        start_date: str,
        end_date: str,
        dimensions: list[str] = None
    ) -> dict:
        """
        Возвращает реалистичные тестовые данные.
        Данные генерируются случайно но в разумных диапазонах.
        """

        # Базовые значения для каждой метрики
        base_values = {
            "activeUsers": random.randint(8000, 15000),
            "sessions": random.randint(12000, 20000),
            "screenPageViews": random.randint(30000, 60000),
            "bounceRate": round(random.uniform(0.35, 0.65), 4),
            "averageSessionDuration": random.randint(120, 300),
            "newUsers": random.randint(5000, 10000),
            "totalRevenue": round(random.uniform(15000, 45000), 2),
        }

        # Если нет dimensions, возвращаем просто суммарные значения
        if not dimensions:
            result = {
                "property_id": self.property_id,
                "date_range": {"start": start_date, "end": end_date},
                "rows": []
            }

            row = {}
            for metric in metrics:
                if metric in base_values:
                    row[metric] = base_values[metric]
                else:
                    row[metric] = 0

            result["rows"].append(row)
            return result

        # Если есть dimensions, генерируем несколько строк
        result = {
            "property_id": self.property_id,
            "date_range": {"start": start_date, "end": end_date},
            "dimensions": dimensions,
            "rows": []
        }

        if "date" in dimensions:
            # Генерируем данные по дням
            days = self._get_days_count(start_date, end_date)
            for i in range(min(days, 30)):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
                row = {"date": date}
                for metric in metrics:
                    if metric in base_values:
                        # Небольшая вариация для каждого дня
                        row[metric] = int(base_values[metric] / days * random.uniform(0.7, 1.3))
                result["rows"].append(row)

        elif "country" in dimensions:
            countries = [
                ("United States", 0.35),
                ("United Kingdom", 0.12),
                ("Germany", 0.09),
                ("France", 0.07),
                ("Canada", 0.06),
                ("Australia", 0.05),
                ("Other", 0.26),
            ]
            for country, share in countries:
                row = {"country": country}
                for metric in metrics:
                    if metric in base_values:
                        row[metric] = int(base_values[metric] * share * random.uniform(0.9, 1.1))
                result["rows"].append(row)

        elif "deviceCategory" in dimensions:
            devices = [
                ("mobile", 0.55),
                ("desktop", 0.38),
                ("tablet", 0.07),
            ]
            for device, share in devices:
                row = {"deviceCategory": device}
                for metric in metrics:
                    if metric in base_values:
                        row[metric] = int(base_values[metric] * share)
                result["rows"].append(row)

        elif "sessionSource" in dimensions:
            sources = [
                ("google", 0.45),
                ("direct", 0.25),
                ("facebook.com", 0.10),
                ("instagram.com", 0.08),
                ("email", 0.07),
                ("other", 0.05),
            ]
            for source, share in sources:
                row = {"sessionSource": source}
                for metric in metrics:
                    if metric in base_values:
                        row[metric] = int(base_values[metric] * share)
                result["rows"].append(row)

        return result

    def _real_query(
        self,
        metrics: list[str],
        start_date: str,
        end_date: str,
        dimensions: list[str] = None
    ) -> dict:
        """
        Реальный запрос к GA4 API.
        Используется когда USE_MOCK=False.
        """
        request = self.RunReportRequest(
            property=f"properties/{self.property_id}",
            date_ranges=[self.DateRange(start_date=start_date, end_date=end_date)],
            metrics=[self.Metric(name=m) for m in metrics],
            dimensions=[self.Dimension(name=d) for d in (dimensions or [])],
        )

        response = self.client.run_report(request)

        rows = []
        for row in response.rows:
            result_row = {}

            for i, dim_value in enumerate(row.dimension_values):
                result_row[dimensions[i]] = dim_value.value

            for i, metric_value in enumerate(row.metric_values):
                try:
                    result_row[metrics[i]] = float(metric_value.value)
                except ValueError:
                    result_row[metrics[i]] = metric_value.value

            rows.append(result_row)

        return {
            "property_id": self.property_id,
            "date_range": {"start": start_date, "end": end_date},
            "rows": rows
        }

    def _get_days_count(self, start_date: str, end_date: str) -> int:
        """Вычисляет количество дней между датами."""
        relative_map = {
            "today": 0,
            "yesterday": 1,
            "7daysAgo": 7,
            "14daysAgo": 14,
            "28daysAgo": 28,
            "30daysAgo": 30,
            "90daysAgo": 90,
        }

        if start_date in relative_map:
            return relative_map[start_date]

        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            return (end - start).days + 1
        except ValueError:
            return 30