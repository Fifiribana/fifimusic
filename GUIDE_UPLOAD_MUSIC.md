# 🎵 Guide d'Upload de Vos Créations Musicales - US EXPLO

## 🚀 **Comment Ajouter Vos Pistes Musicales**

### **Étape 1 : Accès à l'Administration**

1. **Ouvrez US EXPLO** : http://localhost:3000
2. **Connectez-vous** :
   - Cliquez sur l'icône utilisateur dans la navigation
   - **Créez un compte** ou connectez-vous
   - Utilisez n'importe quel email/mot de passe pour tester

3. **Accédez à l'admin** :
   - Une fois connecté, cliquez sur **"Mes Créations"** dans le menu
   - Ou allez directement sur : http://localhost:3000/admin

### **Étape 2 : Interface d'Upload**

Vous verrez une interface moderne avec :
- **Bouton "Ajouter une nouvelle piste"** pour commencer l'upload
- **Liste de vos créations existantes** 
- **Système de gestion complet**

### **Étape 3 : Formulaire d'Upload**

Cliquez sur **"Ajouter une nouvelle piste"** et remplissez :

#### **📝 Informations de Base**
- **Titre** : Le nom de votre piste
- **Région** : Afrique, Asie, Europe, etc.  
- **Style** : Bikutsi Moderne, Makossa, etc.
- **Instrument** : Ex: "Balafon + Synthé"
- **BPM** : Tempo de votre piste
- **Prix** : Prix de vente en euros
- **Humeur** : Énergique, Spirituel, Dansant, etc.
- **Description** : Présentez votre création

#### **📁 Fichiers à Uploader**

1. **Fichier Audio Principal** * (obligatoire)
   - Formats acceptés : MP3, WAV, FLAC
   - Votre piste complète
   - La durée sera détectée automatiquement

2. **Image de Couverture** * (obligatoire)  
   - Formats acceptés : JPG, PNG
   - Artwork/photo pour votre piste
   - Taille recommandée : 500x500px minimum

3. **Aperçu 30s** (optionnel)
   - Version courte pour la prévisualisation
   - Si non fourni, l'audio principal sera utilisé

### **Étape 4 : Publication**

1. **Vérifiez** toutes les informations
2. **Cliquez sur "Publier ma création"**  
3. **Attendez** l'upload (peut prendre quelques minutes selon la taille)
4. **Confirmation** : Vous verrez une notification de succès

### **Étape 5 : Gestion de Vos Pistes**

Dans la section **"Mes Créations"** :
- **Visualisez** toutes vos pistes publiées
- **Écoutez** les aperçus directement
- **Supprimez** si nécessaire
- **Voyez les statistiques** (likes, téléchargements)

## 🔧 **API pour Upload Automatique (Avancé)**

Si vous préférez utiliser l'API directement :

```bash
# 1. Se connecter et obtenir un token
curl -X POST "http://localhost:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "votre@email.com", "password": "motdepasse"}'

# 2. Uploader une piste avec fichiers
curl -X POST "http://localhost:8001/api/tracks/upload" \
  -H "Authorization: Bearer VOTRE_TOKEN" \
  -F "title=Ma Nouvelle Piste" \
  -F "region=Afrique" \
  -F "style=Bikutsi Moderne" \
  -F "price=4.99" \
  -F "audio_file=@/chemin/vers/votre-audio.mp3" \
  -F "image_file=@/chemin/vers/votre-cover.jpg"
```

## 📁 **Organisation Recommandée de Vos Fichiers**

```
📂 Mes Créations/
├── 🎵 Audio/
│   ├── piste1-complete.mp3
│   ├── piste1-preview.mp3
│   ├── piste2-complete.wav
│   └── piste2-preview.mp3
└── 🖼️ Covers/
    ├── piste1-cover.jpg
    ├── piste2-cover.png
    └── album-cover.jpg
```

## ✨ **Conseils pour de Meilleurs Résultats**

### **🎵 Audio**
- **Qualité** : Utilisez des fichiers haute qualité (320kbps minimum)
- **Aperçus** : Créez des extraits de 30s des meilleures parties
- **Formats** : MP3 pour la compatibilité, FLAC pour la qualité maximale

### **🖼️ Images**
- **Résolution** : Minimum 500x500px (idéal 1000x1000px)
- **Format** : JPG ou PNG
- **Style** : Cohérent avec l'univers US EXPLO (couleurs terre, moderne)

### **📝 Métadonnées**
- **Descriptions** : Détaillées et engageantes
- **Tags** : Utilisez des mots-clés recherchables
- **Prix** : Adaptés à votre marché (3-6€ pour des créations originales)

## 🎯 **Visibilité de Vos Créations**

Une fois uploadées, vos pistes apparaîtront :
- ✅ Dans la **recherche générale** du site
- ✅ Sur la **carte interactive** par région
- ✅ Dans votre **page artiste Simon Messela**
- ✅ Dans les **collections thématiques** appropriées
- ✅ Dans les **statistiques** du site

## 🆘 **Support**

Si vous rencontrez des problèmes :
1. **Vérifiez** que vous êtes bien connecté
2. **Contrôlez** les formats de fichiers acceptés  
3. **Assurez-vous** que vos fichiers ne sont pas trop volumineux
4. **Rechargez** la page si nécessaire

---

**🎵 Votre musique mérite d'être entendue dans le monde entier !**
**US EXPLO - "Discover the Pulse of the World" 🌍**