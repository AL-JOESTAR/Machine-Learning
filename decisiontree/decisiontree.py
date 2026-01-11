import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import f1_score
from sklearn.preprocessing import LabelEncoder

# Baca dataset
df = pd.read_csv('healthcare_dataset.csv')

# Drop kolom yang tidak relevan
X = df.drop(columns=[
    'Test Results', 'Name', 'Doctor', 'Hospital', 'Insurance Provider', 'Date of Admission', 'Discharge Date'
])
y = df['Test Results']

# Encode kolom kategori yang penting
le = LabelEncoder()
X['Gender'] = le.fit_transform(X['Gender'])
X['Admission Type'] = le.fit_transform(X['Admission Type'])
X['Medication'] = le.fit_transform(X['Medication'])
X['Medical Condition'] = le.fit_transform(X['Medical Condition'])
X['Blood Type'] = le.fit_transform(X['Blood Type'])

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = DecisionTreeClassifier()
model.fit(X_train, y_train)

# Prediksi dan hitung F1 Score
prediksi = model.predict(X_test)
f1 = f1_score(y_test, prediksi, average='weighted')  # pakai weighted jika multiclass
print(f"F1 Score Model: {f1 * 100:.2f}%")
