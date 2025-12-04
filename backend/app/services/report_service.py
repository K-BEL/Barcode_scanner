"""Sales reporting service using raw MySQL queries."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.core.database import get_db
from app.core.logging import logger


class ReportService:
    """Service for sales reporting operations."""
    
    def get_daily_sales(
        self,
        date: Optional[str] = None,
        cashier_name: Optional[str] = None
    ) -> Dict:
        """
        Get daily sales report.
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            cashier_name: Optional cashier name filter
            
        Returns:
            Daily sales summary
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            where_clauses = ["DATE(created_at) = %s"]
            params = [date]
            
            if cashier_name:
                where_clauses.append("cashier_name = %s")
                params.append(cashier_name)
            
            # Get total sales
            query = f"""
                SELECT 
                    COUNT(*) as total_bills,
                    SUM(subtotal) as total_subtotal,
                    SUM(discount_amount) as total_discount,
                    SUM(tax_amount) as total_tax,
                    SUM(total_amount) as total_amount,
                    AVG(total_amount) as avg_bill_amount
                FROM bills
                WHERE {' AND '.join(where_clauses)}
            """
            cursor.execute(query, params)
            summary = cursor.fetchone()
            
            # Get payment method breakdown
            query = f"""
                SELECT 
                    payment_method,
                    COUNT(*) as count,
                    SUM(total_amount) as total
                FROM bills
                WHERE {' AND '.join(where_clauses)}
                GROUP BY payment_method
            """
            cursor.execute(query, params)
            payment_methods = cursor.fetchall()
            
            # Get top products sold (from bill_text - simplified)
            # In a real system, you'd have a bill_items table
            cursor.close()
            
            return {
                "date": date,
                "cashier": cashier_name,
                "summary": {
                    "total_bills": summary['total_bills'] or 0,
                    "total_subtotal": float(summary['total_subtotal'] or 0),
                    "total_discount": float(summary['total_discount'] or 0),
                    "total_tax": float(summary['total_tax'] or 0),
                    "total_amount": float(summary['total_amount'] or 0),
                    "avg_bill_amount": float(summary['avg_bill_amount'] or 0)
                },
                "payment_methods": [
                    {
                        "method": pm['payment_method'],
                        "count": pm['count'],
                        "total": float(pm['total'])
                    }
                    for pm in payment_methods
                ]
            }
    
    def get_weekly_sales(
        self,
        week_start: Optional[str] = None,
        cashier_name: Optional[str] = None
    ) -> Dict:
        """
        Get weekly sales report.
        
        Args:
            week_start: Start date in YYYY-MM-DD format (defaults to start of current week)
            cashier_name: Optional cashier name filter
            
        Returns:
            Weekly sales summary
        """
        if not week_start:
            today = datetime.now()
            days_since_monday = today.weekday()
            week_start_date = today - timedelta(days=days_since_monday)
            week_start = week_start_date.strftime('%Y-%m-%d')
        
        week_end_date = datetime.strptime(week_start, '%Y-%m-%d') + timedelta(days=6)
        week_end = week_end_date.strftime('%Y-%m-%d')
        
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            where_clauses = ["DATE(created_at) >= %s", "DATE(created_at) <= %s"]
            params = [week_start, week_end]
            
            if cashier_name:
                where_clauses.append("cashier_name = %s")
                params.append(cashier_name)
            
            # Get total sales
            query = f"""
                SELECT 
                    COUNT(*) as total_bills,
                    SUM(subtotal) as total_subtotal,
                    SUM(discount_amount) as total_discount,
                    SUM(tax_amount) as total_tax,
                    SUM(total_amount) as total_amount,
                    AVG(total_amount) as avg_bill_amount
                FROM bills
                WHERE {' AND '.join(where_clauses)}
            """
            cursor.execute(query, params)
            summary = cursor.fetchone()
            
            # Get daily breakdown
            query = f"""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as count,
                    SUM(total_amount) as total
                FROM bills
                WHERE {' AND '.join(where_clauses)}
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """
            cursor.execute(query, params)
            daily_breakdown = cursor.fetchall()
            
            cursor.close()
            
            return {
                "week_start": week_start,
                "week_end": week_end,
                "cashier": cashier_name,
                "summary": {
                    "total_bills": summary['total_bills'] or 0,
                    "total_subtotal": float(summary['total_subtotal'] or 0),
                    "total_discount": float(summary['total_discount'] or 0),
                    "total_tax": float(summary['total_tax'] or 0),
                    "total_amount": float(summary['total_amount'] or 0),
                    "avg_bill_amount": float(summary['avg_bill_amount'] or 0)
                },
                "daily_breakdown": [
                    {
                        "date": str(row['date']),
                        "count": row['count'],
                        "total": float(row['total'])
                    }
                    for row in daily_breakdown
                ]
            }
    
    def get_monthly_sales(
        self,
        year: int,
        month: int,
        cashier_name: Optional[str] = None
    ) -> Dict:
        """
        Get monthly sales report.
        
        Args:
            year: Year (e.g., 2024)
            month: Month (1-12)
            cashier_name: Optional cashier name filter
            
        Returns:
            Monthly sales summary
        """
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            
            where_clauses = ["YEAR(created_at) = %s", "MONTH(created_at) = %s"]
            params = [year, month]
            
            if cashier_name:
                where_clauses.append("cashier_name = %s")
                params.append(cashier_name)
            
            # Get total sales
            query = f"""
                SELECT 
                    COUNT(*) as total_bills,
                    SUM(subtotal) as total_subtotal,
                    SUM(discount_amount) as total_discount,
                    SUM(tax_amount) as total_tax,
                    SUM(total_amount) as total_amount,
                    AVG(total_amount) as avg_bill_amount
                FROM bills
                WHERE {' AND '.join(where_clauses)}
            """
            cursor.execute(query, params)
            summary = cursor.fetchone()
            
            # Get cashier breakdown
            query = f"""
                SELECT 
                    cashier_name,
                    COUNT(*) as count,
                    SUM(total_amount) as total
                FROM bills
                WHERE {' AND '.join(where_clauses)}
                GROUP BY cashier_name
                ORDER BY total DESC
            """
            cursor.execute(query, params)
            cashier_breakdown = cursor.fetchall()
            
            cursor.close()
            
            return {
                "year": year,
                "month": month,
                "summary": {
                    "total_bills": summary['total_bills'] or 0,
                    "total_subtotal": float(summary['total_subtotal'] or 0),
                    "total_discount": float(summary['total_discount'] or 0),
                    "total_tax": float(summary['total_tax'] or 0),
                    "total_amount": float(summary['total_amount'] or 0),
                    "avg_bill_amount": float(summary['avg_bill_amount'] or 0)
                },
                "cashier_breakdown": [
                    {
                        "cashier": row['cashier_name'] or "Unknown",
                        "count": row['count'],
                        "total": float(row['total'])
                    }
                    for row in cashier_breakdown
                ]
            }

