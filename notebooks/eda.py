import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load cleaned dataset
df = pd.read_csv(r"C:\Users\acer\Downloads\FounderFlow\dataset\cleaned_startup_valuation_dataset.csv")

# Create folder for graphs
os.makedirs("EDA_Graphs", exist_ok=True)

print("=" * 60)
print("DATASET INFORMATION")
print("=" * 60)
print(df.info())

print("\nDataset Shape:", df.shape)

print("\nSummary Statistics:")
print(df.describe())

# -----------------------------
# 1. Startup Exit Distribution
# -----------------------------
plt.figure(figsize=(6,5))
sns.countplot(x="exited", data=df)
plt.title("Startup Exit Distribution")
plt.savefig("EDA_Graphs/1_Startup_Exit_Distribution.png")
plt.close()

# -----------------------------
# 2. Funding Amount Distribution
# -----------------------------
plt.figure(figsize=(8,5))
sns.histplot(df["funding_amount_usd"], bins=30)
plt.title("Funding Amount Distribution")
plt.savefig("EDA_Graphs/2_Funding_Distribution.png")
plt.close()

# -----------------------------
# 3. Employee Count Distribution
# -----------------------------
plt.figure(figsize=(8,5))
sns.histplot(df["employee_count"], bins=30)
plt.title("Employee Count Distribution")
plt.savefig("EDA_Graphs/3_Employee_Count.png")
plt.close()

# -----------------------------
# 4. Founded Year Distribution
# -----------------------------
plt.figure(figsize=(8,5))
sns.countplot(x="founded_year", data=df)
plt.xticks(rotation=90)
plt.title("Founded Year Distribution")
plt.savefig("EDA_Graphs/4_Founded_Year.png")
plt.close()

# -----------------------------
# 5. Funding Year Distribution
# -----------------------------
plt.figure(figsize=(8,5))
sns.countplot(x="funding_year", data=df)
plt.xticks(rotation=90)
plt.title("Funding Year Distribution")
plt.savefig("EDA_Graphs/5_Funding_Year.png")
plt.close()

# -----------------------------
# 6. Top Industries
# -----------------------------
plt.figure(figsize=(10,5))
df["industry"].value_counts().head(10).plot(kind="bar")
plt.title("Top Industries")
plt.savefig("EDA_Graphs/6_Top_Industries.png")
plt.close()

# -----------------------------
# 7. Top Countries
# -----------------------------
plt.figure(figsize=(10,5))
df["country"].value_counts().head(10).plot(kind="bar")
plt.title("Top Countries")
plt.savefig("EDA_Graphs/7_Top_Countries.png")
plt.close()

# -----------------------------
# 8. Exit Type Distribution
# -----------------------------
plt.figure(figsize=(8,5))
df["exit_type"].value_counts().plot(kind="bar")
plt.title("Exit Type Distribution")
plt.savefig("EDA_Graphs/8_Exit_Type.png")
plt.close()

# -----------------------------
# 9. Correlation Heatmap
# -----------------------------
plt.figure(figsize=(12,10))
sns.heatmap(df.corr(), cmap="coolwarm")
plt.title("Correlation Heatmap")
plt.savefig("EDA_Graphs/9_Correlation_Heatmap.png")
plt.close()

# -----------------------------
# 10. Correlation with Target
# -----------------------------
corr = df.corr()["exited"].sort_values(ascending=False)

plt.figure(figsize=(8,8))
corr.plot(kind="bar")
plt.title("Correlation with Startup Exit")
plt.savefig("EDA_Graphs/10_Target_Correlation.png")
plt.close()

# -----------------------------
# 11. Funding vs Exit
# -----------------------------
plt.figure(figsize=(7,5))
sns.boxplot(x="exited", y="funding_amount_usd", data=df)
plt.title("Funding Amount vs Exit")
plt.savefig("EDA_Graphs/11_Funding_vs_Exit.png")
plt.close()

# -----------------------------
# 12. Revenue vs Exit
# -----------------------------
plt.figure(figsize=(7,5))
sns.boxplot(x="exited", y="estimated_revenue_usd", data=df)
plt.title("Revenue vs Exit")
plt.savefig("EDA_Graphs/12_Revenue_vs_Exit.png")
plt.close()

# -----------------------------
# 13. Valuation vs Exit
# -----------------------------
plt.figure(figsize=(7,5))
sns.boxplot(x="exited", y="estimated_valuation_usd", data=df)
plt.title("Valuation vs Exit")
plt.savefig("EDA_Graphs/13_Valuation_vs_Exit.png")
plt.close()

print("\nTop Feature Correlations with Target:")
print(corr)

print("\nEDA Completed Successfully!")
print("Graphs saved in 'EDA_Graphs' folder.")
