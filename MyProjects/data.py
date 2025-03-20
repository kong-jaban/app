import pandas as pd
import random
from faker import Faker
import datetime

# Initialize Faker
fake = Faker()

# Number of customer data to generate
num_records = 1000

# Lists to hold customer data
names = []
ages = []
genders = []
emails = []
join_dates = []
purchase_counts = []
total_spent = []

# Generate customer data
for _ in range(num_records):
    names.append(fake.name())
    ages.append(random.randint(18, 65))
    genders.append(random.choice(['남성', '여성']))
    emails.append(fake.email())
    join_dates.append(fake.date_this_decade())
    purchase_counts.append(random.randint(1, 50))
    total_spent.append(round(random.uniform(50000, 5000000), 2))

# Create DataFrame
customer_data = pd.DataFrame({
    '이름': names,
    '나이': ages,
    '성별': genders,
    '이메일': emails,
    '가입일': join_dates,
    '구매횟수': purchase_counts,
    '총 구매금액': total_spent
})

# Save to CSV file
file_path = "customer_data.csv"
customer_data.to_csv(file_path, index=False)

print(f"CSV file created: {file_path}")
