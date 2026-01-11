import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score


X = [[1],[2],[3],[4],[5],[6],[7],[8],[9],[10],[11],[12],[13]]
y =[40,50,75,80,90,95,96,97,98,99,88,80,73]


X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.2, random_state=42)

model = KNeighborsRegressor(n_neighbors=10)
model.fit(X_train, y_train)

prediksi = model.predict(X_test)
mse = mean_squared_error(y_test, prediksi)
r2 = r2_score(y_test, prediksi)
# print(f"Akurasi Model: {r2 * 100:.2f}%")

jam_belajar = float(input("Masukkan jumlah jam belajar per hari: "))
X_baru = [[jam_belajar]]
nilai_prediksi = model.predict(X_baru)[0]
print(f"Prediksi nilai kamu: {nilai_prediksi:.2f}")
