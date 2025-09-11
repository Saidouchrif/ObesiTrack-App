// Script d'initialisation MongoDB pour ObesiTrack
db = db.getSiblingDB('obesitrack');

// Créer les collections
db.createCollection('Users');
db.createCollection('Predict');
db.createCollection('Result');

// Créer un utilisateur admin par défaut
db.Users.insertOne({
    email: "admin@obesitrack.com",
    name: "Administrateur",
    password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8Kz2", // motdepasse123
    Role: "admin",
    created_at: new Date(),
    updated_at: new Date()
});

// Créer des index pour optimiser les performances
db.Users.createIndex({ "email": 1 }, { unique: true });
db.Predict.createIndex({ "user_id": 1 });
db.Predict.createIndex({ "created_at": -1 });
db.Result.createIndex({ "user_id": 1 });
db.Result.createIndex({ "predict_id": 1 });
db.Result.createIndex({ "created_at": -1 });

print("✅ Base de données ObesiTrack initialisée avec succès");
print("👤 Utilisateur admin créé: admin@obesitrack.com / motdepasse123");
