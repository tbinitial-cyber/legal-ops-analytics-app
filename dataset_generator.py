import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import timedelta

fake = Faker()

NUM_MATTERS = 3000
NUM_REQUESTS = 4000
NUM_CASES = 1500

law_firms = [
"Skadden","Latham & Watkins","Clifford Chance","Freshfields",
"Allen & Overy","Linklaters","White & Case","Hogan Lovells",
"DLA Piper","Baker & McKenzie"
]

firm_multiplier = {
"Skadden":1.4,
"Latham & Watkins":1.35,
"Clifford Chance":1.3,
"Freshfields":1.25,
"Allen & Overy":1.2,
"Linklaters":1.2,
"White & Case":1.15,
"Hogan Lovells":1.1,
"DLA Piper":1.05,
"Baker & McKenzie":1.0
}

role_rates = {
"Partner":900,
"Associate":450
}

practice_areas = ["Employment","IP","Compliance","Commercial"]
matter_types = ["Contract","Litigation","Regulatory"]
business_units = ["Sales","Product","HR","Finance","Compliance"]
regions = ["US","EU","APAC"]
complexity_levels = ["Low","Medium","High"]

# ---------------------
# MASTER MATTER TABLE
# ---------------------

matters=[]

for i in range(NUM_MATTERS):

    open_date = fake.date_between(start_date="-2y", end_date="-6m")

    status=random.choice(["Open","Closed"])

    if status=="Closed":
        duration=random.randint(30,400)
        close_date=open_date+timedelta(days=duration)
    else:
        close_date=None

    exposure=random.randint(50000,5000000)

    matters.append({

    "matter_id":f"M-{1000+i}",
    "matter_type":random.choice(matter_types),
    "practice_area":random.choice(practice_areas),
    "business_unit":random.choice(business_units),
    "region":random.choice(regions),
    "matter_complexity":random.choice(complexity_levels),
    "financial_exposure":exposure,
    "internal_lawyer":fake.name(),
    "open_date":open_date,
    "close_date":close_date,
    "matter_status":status
    })

matter_df=pd.DataFrame(matters)

# ---------------------
# LEGAL SPEND TABLE
# ---------------------

spend=[]

for i in range(NUM_MATTERS):

    matter=random.choice(matter_df["matter_id"])
    firm=random.choice(law_firms)
    role=random.choice(["Partner","Associate"])

    base_rate=role_rates[role]
    multiplier=firm_multiplier[firm]

    rate=base_rate*multiplier

    hours=max(5,np.random.normal(40,15))

    invoice=hours*rate

    violation=random.choice(["None","Travel Billing","Excess Research"])

    if violation=="Travel Billing":
        savings=invoice*0.20
    elif violation=="Excess Research":
        savings=invoice*0.15
    else:
        savings=0

    approved=invoice-savings

    budget=invoice*random.uniform(0.8,1.2)

    spend.append({

    "matter_id":matter,
    "law_firm":firm,
    "timekeeper_role":role,
    "hours_billed":round(hours,2),
    "hourly_rate":round(rate,2),
    "invoice_amount":round(invoice,2),
    "savings":round(savings,2),
    "approved_invoice_amount":round(approved,2),
    "budget_allocated":round(budget,2),
    "budget_variance":round(invoice-budget,2),
    "billing_violation_type":violation,
    "invoice_date":fake.date_between(start_date="-2y", end_date="today")

    })

legal_spend_df=pd.DataFrame(spend)

# ---------------------
# WORKFLOW DATA
# ---------------------

workflow=[]

for i in range(NUM_REQUESTS):

    matter=random.choice(matter_df["matter_id"])

    submission=fake.date_between(start_date="-1y", end_date="today")

    complexity=random.choice(complexity_levels)

    automation=random.choice(["Yes","No"])

    base_days={"Low":2,"Medium":5,"High":10}

    review_days=base_days[complexity]

    if automation=="Yes":
        review_days*=random.uniform(0.5,0.8)

    completion=submission+timedelta(days=int(review_days))

    sla=random.choice([3,5,7])

    sla_met=(completion-submission).days<=sla

    workflow.append({

    "request_id":f"R-{2000+i}",
    "matter_id":matter,
    "request_type":random.choice(["NDA","Vendor Contract","Employment Issue","Regulatory Review"]),
    "priority":random.choice(["Low","Medium","High"]),
    "automation_used":automation,
    "review_time_days":(completion-submission).days,
    "sla_target_days":sla,
    "sla_met":sla_met
    })

workflow_df=pd.DataFrame(workflow)

# ---------------------
# LITIGATION DATA
# ---------------------

cases=[]

for i in range(NUM_CASES):

    matter=random.choice(matter_df["matter_id"])

    complexity=random.choice(complexity_levels)

    duration={"Low":120,"Medium":240,"High":480}[complexity]

    cost=duration*random.randint(100,400)

    outcome=random.choice(["Won","Lost","Settled"])

    settlement=cost*random.uniform(0.3,0.7) if outcome=="Settled" else 0

    cases.append({

    "case_id":f"C-{3000+i}",
    "matter_id":matter,
    "case_type":random.choice(["Employment","Commercial","Regulatory","IP"]),
    "case_complexity":complexity,
    "legal_cost":round(cost,2),
    "case_outcome":outcome,
    "settlement_amount":round(settlement,2)

    })

cases_df=pd.DataFrame(cases)

# ---------------------
# SAVE FILES
# ---------------------

matter_df.to_csv("matter_master_dataset.csv",index=False)
legal_spend_df.to_csv("legal_spend_dataset.csv",index=False)
workflow_df.to_csv("legal_workflow_dataset.csv",index=False)
cases_df.to_csv("litigation_dataset.csv",index=False)

print("All Legal Ops synthetic datasets created.")