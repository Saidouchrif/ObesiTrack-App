#!/usr/bin/env python3
"""
Script pour entraîner le modèle de prédiction d'obésité
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def train_obesity_model():
    """Entraîne le modèle de prédiction d'obésité"""
    
    print("=== ENTRAÎNEMENT DU MODÈLE DE PRÉDICTION D'OBÉSITÉ ===")
    
    # Chargement des données
    print("Chargement des données...")
    df = pd.read_csv('Data.csv')
    print(f"Dataset chargé: {df.shape[0]} lignes, {df.shape[1]} colonnes")
    
    # Préprocessing
    print("Préprocessing des données...")
    df_processed = df.copy()
    
    # Encodage des variables catégorielles
    label_encoders = {}
    categorical_features = ['Gender', 'family_history_with_overweight', 'FAVC', 'CAEC', 'SMOKE', 'SCC', 'CALC', 'MTRANS']
    
    for feature in categorical_features:
        le = LabelEncoder()
        df_processed[feature] = le.fit_transform(df_processed[feature])
        label_encoders[feature] = le
        print(f"  ✓ Encodé {feature}")
    
    # Encodage de la variable cible
    target_encoder = LabelEncoder()
    df_processed['NObeyesdad_encoded'] = target_encoder.fit_transform(df_processed['NObeyesdad'])
    print(f"  ✓ Encodé variable cible: {dict(zip(target_encoder.classes_, target_encoder.transform(target_encoder.classes_)))}")
    
    # Préparation des features
    feature_columns = [col for col in df_processed.columns if col not in ['NObeyesdad', 'NObeyesdad_encoded']]
    X = df_processed[feature_columns]
    y = df_processed['NObeyesdad_encoded']
    
    print(f"Features sélectionnées: {len(feature_columns)}")
    
    # Division train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Division train/test: {X_train.shape[0]} train, {X_test.shape[0]} test")
    
    # Normalisation
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print("  ✓ Normalisation effectuée")
    
    # Entraînement des modèles
    print("Entraînement des modèles...")
    
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
        'SVM': SVC(random_state=42, probability=True)
    }
    
    best_model = None
    best_score = 0
    best_name = ""
    
    for name, model in models.items():
        print(f"  Entraînement de {name}...")
        
        # Entraînement
        if name in ['Logistic Regression', 'SVM']:
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
        
        # Évaluation
        accuracy = accuracy_score(y_test, y_pred)
        print(f"    Accuracy: {accuracy:.4f}")
        
        if accuracy > best_score:
            best_score = accuracy
            best_model = model
            best_name = name
    
    print(f"\nMeilleur modèle: {best_name} (Accuracy: {best_score:.4f})")
    
    # Sauvegarde
    print("Sauvegarde des modèles...")
    os.makedirs('models', exist_ok=True)
    
    # Sauvegarde du meilleur modèle
    joblib.dump(best_model, 'models/best_obesity_model.pkl')
    print("  ✓ Modèle sauvegardé")
    
    # Sauvegarde du scaler
    joblib.dump(scaler, 'models/scaler.pkl')
    print("  ✓ Scaler sauvegardé")
    
    # Sauvegarde des encodeurs
    joblib.dump(label_encoders, 'models/label_encoders.pkl')
    print("  ✓ Label encoders sauvegardés")
    
    # Sauvegarde de l'encodeur de la variable cible
    joblib.dump(target_encoder, 'models/target_encoder.pkl')
    print("  ✓ Target encoder sauvegardé")
    
    # Sauvegarde des noms des features
    joblib.dump(feature_columns, 'models/feature_columns.pkl')
    print("  ✓ Feature columns sauvegardées")
    
    # Rapport final
    print(f"\n=== RAPPORT FINAL ===")
    print(f"Modèle sélectionné: {best_name}")
    print(f"Accuracy: {best_score:.4f}")
    print(f"Nombre de features: {len(feature_columns)}")
    print(f"Nombre de classes: {len(target_encoder.classes_)}")
    print(f"Classes: {list(target_encoder.classes_)}")
    
    print("\n✅ Entraînement terminé avec succès!")
    print("Les modèles sont sauvegardés dans le dossier 'models/'")
    
    return best_model, best_score

if __name__ == "__main__":
    train_obesity_model()
