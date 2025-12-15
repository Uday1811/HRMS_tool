
from datetime import date

def payroll_cycle_for(target_date: date):
    """
    Return (start_date, end_date) for the payroll period that contains `target_date`.
    Period runs 28th of previous month → 27th of current month.
    """
    if target_date.day >= 28:
        start = date(target_date.year, target_date.month, 28)
        # end is 27th of next month
        if target_date.month == 12:
            end = date(target_date.year + 1, 1, 27)
        else:
            end = date(target_date.year, target_date.month + 1, 27)
    else:
        # we are in the first part of the cycle (1-27)
        if target_date.month == 1:
            start = date(target_date.year - 1, 12, 28)
        else:
            start = date(target_date.year, target_date.month - 1, 28)
        end = date(target_date.year, target_date.month, 27)
    return start, end
