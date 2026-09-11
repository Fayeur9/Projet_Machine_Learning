# Guide des métriques d'évaluation

Une métrique = une note donnée au modèle. Le choix dépend du **type de problème**.

| Type de problème | Modèles vus | Aller à |
|---|---|---|
| Régression (prédire un nombre) | Régression linéaire, Arbre / RF regressor | [1. Régression](#1-régression) |
| Classification (prédire une classe) | Régression logistique, Arbre / RF classifier | [2. Classification](#2-classification) |
| Clustering (pas de labels) | K-Means | [3. Clustering](#3-clustering) |

---

## 1. Régression

On compare la valeur prédite à la vraie valeur. **L'erreur = vraie − prédite.**

### Exemple fil rouge — prix de 4 appartements (en k€)

| Vrai | Prédit | Erreur |
|---|---|---|
| 200 | 190 | 10 |
| 300 | 280 | 20 |
| 150 | 160 | −10 |
| 400 | 300 | 100 |

### MAE — Mean Absolute Error
Moyenne des erreurs **en valeur absolue**.

`MAE = (10 + 20 + 10 + 100) / 4 = 35`

> « En moyenne je me trompe de 35 k€. »

- Même unité que la cible → très facile à expliquer à un client
- Ne punit pas les grosses erreurs plus que les petites

### MSE / RMSE — (Root) Mean Squared Error
On met les erreurs **au carré** avant de moyenner.

`MSE = (100 + 400 + 100 + 10000) / 4 = 2650`
`RMSE = √2650 ≈ 51.5`

> RMSE (51.5) >> MAE (35) : signe qu'il y a **une grosse erreur** qui plombe tout (les 100 k€).

- RMSE est dans l'unité de la cible, MSE non (k€²)
- Punit fort les grosses erreurs → à utiliser quand une grosse erreur coûte cher

### R² — coefficient de détermination
« Quel % de la variation mes prédictions expliquent-elles ? »

| R² | Lecture |
|---|---|
| 1.0 | prédictions parfaites |
| 0.8 | le modèle explique 80 % de la variation — bon |
| 0.0 | aussi bon que prédire toujours la moyenne |
| < 0 | **pire** que prédire la moyenne |

- Sans unité → permet de comparer deux problèmes différents
- Toujours le regarder **sur le test**, pas sur le train

### Code
```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

y_pred = model.predict(X_test)

mean_absolute_error(y_test, y_pred)                 # MAE
mean_squared_error(y_test, y_pred)                  # MSE
mean_squared_error(y_test, y_pred) ** 0.5           # RMSE
r2_score(y_test, y_pred)                            # R²
```

### Que choisir ?
- **Par défaut** : RMSE + R² (RMSE pour l'ampleur, R² pour la qualité globale)
- **Beaucoup d'outliers / on veut les ignorer** : MAE
- **Une grosse erreur est inacceptable** : RMSE

---

## 2. Classification

### La matrice de confusion — la base de tout

Exemple : détecter une **maladie** sur 100 patients (positif = malade).

|  | Prédit : sain | Prédit : malade |
|---|---|---|
| **Vrai : sain** | VN = 85 | **FP = 5** (fausse alerte) |
| **Vrai : malade** | **FN = 4** (raté !) | VP = 6 |

- **VP** vrai positif — malade détecté ✅
- **VN** vrai négatif — sain déclaré sain ✅
- **FP** faux positif — fausse alerte ❌
- **FN** faux négatif — malade **non détecté** ❌

Toutes les métriques ci-dessous sont juste des combinaisons de ces 4 nombres.

### Accuracy — taux de bonnes réponses
`(VP + VN) / total = (6 + 85) / 100 = 91 %`

> ⚠️ **Le piège classique.** Ici, un modèle qui dit « tout le monde est sain » ferait 90 % d'accuracy sans détecter un seul malade. **Sur données déséquilibrées, l'accuracy ment.**

### Precision — « quand je dis oui, ai-je raison ? »
`VP / (VP + FP) = 6 / (6 + 5) = 55 %`

> Sur 11 alertes, 6 étaient justes.

À privilégier quand une **fausse alerte coûte cher** : spam (mail important en spam), suspension de compte, notification marketing.

### Recall (rappel) — « ai-je trouvé tous les positifs ? »
`VP / (VP + FN) = 6 / (6 + 4) = 60 %`

> Sur 10 vrais malades, j'en ai trouvé 6. J'en ai **raté 4**.

À privilégier quand **rater un positif coûte cher** : maladie, fraude bancaire, panne, churn client.

> 🔑 **Precision vs Recall, c'est un arbitrage.** Baisser le seuil de décision → plus de recall, moins de precision. Et inversement. On ne peut pas tout maximiser.

### F1-score — le compromis
Moyenne harmonique de precision et recall.

`F1 = 2 × (0.55 × 0.60) / (0.55 + 0.60) ≈ 0.57`

- Élevé **seulement si les deux** sont élevés (contrairement à une moyenne simple)
- La métrique par défaut quand les classes sont déséquilibrées

### ROC-AUC
Mesure la capacité à **séparer** les deux classes, tous seuils confondus.

| AUC | Lecture |
|---|---|
| 1.0 | séparation parfaite |
| 0.9 | très bon |
| 0.7 | correct |
| 0.5 | aléatoire (pile ou face) |

> Interprétation : « probabilité que le modèle donne un score plus élevé à un malade tiré au hasard qu'à un sain tiré au hasard. »

Utile pour **comparer deux modèles** indépendamment du seuil choisi.

### Code
```python
from sklearn.metrics import (confusion_matrix, classification_report)

y_pred = model.predict(X_test)

print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))   # ⭐ tout d'un coup

roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])   # ⚠️ proba, pas predict
```

`classification_report` donne precision / recall / f1 pour chaque classe : **commencer par là.**

### Que choisir ?
| Situation | Métrique |
|---|---|
| Classes équilibrées, erreurs de même coût | Accuracy |
| Fausse alerte coûteuse | Precision |
| Positif raté coûteux (fraude, maladie) | Recall |
| Déséquilibré, pas de préférence | F1 |
| Comparer des modèles | ROC-AUC |

---

## 3. Clustering (K-Means)

Pas de vraie réponse → on mesure la **qualité des groupes**, pas l'exactitude.

### Inertie (WCSS) + méthode du coude
Somme des distances² entre chaque point et le centre de son cluster. **Plus c'est bas, mieux c'est** — mais elle baisse toujours quand k augmente (avec k = n points, inertie = 0).

On trace l'inertie en fonction de k et on cherche le **coude** : le point où ça arrête de bien descendre.

```
inertie
 |  •
 |    •
 |      •
 |        •___     ← le coude : k = 4
 |            •___•___•
 +-------------------------- k
   1  2  3  4  5  6  7
```

```python
inerties = []
for k in range(1, 10):
    km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X)
    inerties.append(km.inertia_)

plt.plot(range(1, 10), inerties, marker='o')
```

### Silhouette — la plus fiable
Pour chaque point : est-il plus proche de son cluster que du cluster voisin ?

| Score | Lecture |
|---|---|
| ~ 1 | clusters bien séparés 👍 |
| ~ 0 | points à la frontière, clusters qui se touchent |
| < 0 | points mal classés, mauvais clustering |

```python
from sklearn.metrics import silhouette_score
silhouette_score(X, km.labels_)     # > 0.5 = bon
```

> 💡 En pratique : coude **+** silhouette. Si les deux pointent vers le même k, on est confiant.

⚠️ K-Means utilise des distances → **toujours scaler** (`StandardScaler`) avant, sinon la variable avec les plus grands nombres écrase tout.

---

## Réflexes à garder

1. **Toujours évaluer sur le test**, jamais sur le train.
2. Un **gros écart train / test** = overfitting (typique des arbres profonds).
3. En classification : **regarder la matrice de confusion** avant les scores.
4. **L'accuracy seule ne suffit jamais** sur données déséquilibrées.
5. Choisir la métrique **selon le coût métier de l'erreur**, pas selon celle qui donne le plus beau chiffre.
6. Dans `GridSearchCV`, la métrique optimisée se choisit avec `scoring=` :
   ```python
   GridSearchCV(pipe, params, cv=5, scoring='f1')     # 'r2', 'recall', 'roc_auc'...
   ```

## Antisèche

| Métrique | Problème | Bon score | En une phrase |
|---|---|---|---|
| MAE | Régression | bas | Erreur moyenne, en unité réelle |
| RMSE | Régression | bas | Comme MAE mais punit les grosses erreurs |
| R² | Régression | → 1 | % de variation expliquée |
| Accuracy | Classification | → 1 | % de bonnes réponses |
| Precision | Classification | → 1 | Mes alertes sont-elles justes ? |
| Recall | Classification | → 1 | Ai-je trouvé tous les positifs ? |
| F1 | Classification | → 1 | Compromis precision / recall |
| ROC-AUC | Classification | → 1 | Capacité à séparer les classes |
| Inertie | Clustering | bas (coude) | Compacité des clusters |
| Silhouette | Clustering | > 0.5 | Clusters bien séparés ? |
