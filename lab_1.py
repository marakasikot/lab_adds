# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

# 1. Генерація модельних даних
np.random.seed(42)

n_users = 1000
n_ads = 30
n_rows = 5000

data = {
    'user_id': np.random.randint(1, n_users + 1, n_rows),
    'ad_id': np.random.randint(1, n_ads + 1, n_rows),
    'views': np.random.randint(1, 20, n_rows),
    'clicks': np.random.poisson(1.5, n_rows),
    'view_time': np.random.uniform(0.5, 10.0, n_rows)
}

df = pd.DataFrame(data)

# 2. Розрахунок метрики "набридання"
df['clicks'] = df['clicks'].clip(upper=df['views'])  # Кліків не більше, ніж переглядів
df['ctr'] = df['clicks'] / df['views']
df['boredom_score'] = (df['views'] / (df['clicks'] + 1)) + (10 / df['view_time'])

# 3. Класифікація: реклама набридла чи ні (1 - так, 0 - ні)
df['is_boring'] = (df['boredom_score'] > 6).astype(int)

# 4. Навчання моделі
features = ['views', 'clicks', 'view_time', 'ctr']
X = df[features]
y = df['is_boring']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# 5. Оцінка моделі
y_pred = model.predict(X_test)

print("== Класифікаційний звіт ==")
print(classification_report(y_test, y_pred))

# 6. Візуалізація розподілу boredom_score
plt.figure(figsize=(10, 5))
plt.hist(df['boredom_score'], bins=50, color='skyblue')
plt.axvline(x=6, color='red', linestyle='--', label='Поріг набридання')
plt.title("Розподіл показника набридання реклами")
plt.xlabel("boredom_score")
plt.ylabel("Кількість прикладів")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
