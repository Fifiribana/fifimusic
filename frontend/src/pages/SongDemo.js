import React from "react";
import { Music, Sparkles, Heart, Clock, Guitar, Volume2, Headphones, Wand2 } from "lucide-react";

const SongDemo = () => {
  // Exemple de chanson générée par l'IA (basée sur les tests backend)
  const demoSong = {
    title: "Les Cœurs Unis",
    inspiration_phrase: "La musique unit les cœurs par-delà les frontières",
    musical_style: "Bikutsi",
    language: "français",
    mood: "inspirant",
    tempo: "modéré",
    lyrics: `[Intro]
Balafon résonne, djembé qui bat
La mélodie voyage, par-delà les pas
Oh oh oh, écoutez bien
La musique nous lie, c'est notre refrain

[Couplet 1]
Depuis Yaoundé jusqu'aux terres lointaines
Chaque cœur qui bat porte nos refraines
Le Bikutsi danse, les âmes s'éveillent
Par-delà les murs, l'amour se dévoile

[Refrain]
La musique unit les cœurs par-delà les frontières
Nos voix se mêlent, nos âmes sont libres et fières
Ensemble nous chantons, ensemble nous vibrons
L'universel langage qui nous fait communion

[Couplet 2]
Les rythmes africains, messagers de paix
Traversent océans, montagnes et forêts
Peu importe la langue, peu importe la terre
Dans cette mélodie, nous sommes tous frères

[Refrain]
La musique unit les cœurs par-delà les frontières
Nos voix se mêlent, nos âmes sont libres et fières
Ensemble nous chantons, ensemble nous vibrons
L'universel langage qui nous fait communion

[Pont]
Quand les tambours battent (tam tam tam)
Nos cœurs se rapprochent (proche, si proche)
Plus de différences, plus de distance
La musique nous donne une nouvelle chance

[Refrain Final]
La musique unit les cœurs par-delà les frontières
Nos voix se mêlent, nos âmes sont libres et fières
Pour l'éternité, nous chanterons
Ce message d'amour que nous porterons

[Outro]
Balafon s'éteint, mais le message demeure
Dans chaque cœur résonne cette douce lueur
Oh oh oh, souvenez-vous bien
La musique nous unit, c'est notre chemin`,
    song_structure: {
      structure: "Intro - Couplet - Refrain - Couplet - Refrain - Pont - Refrain - Outro",
      sections: ["Intro", "Couplet", "Refrain", "Pont", "Outro"],
      estimated_duration: "3-4 minutes"
    },
    chord_suggestions: [
      "Progression principale: Am - F - C - G",
      "Couplets: Am - Dm - G - C",
      "Refrain: F - C - G - Am",
      "Pont: Dm - Am - F - G"
    ],
    arrangement_notes: "Commencer avec le balafon seul, ajouter progressivement djembé, guitare acoustique, et chœurs. Les cuivres peuvent ponctuer le refrain pour plus d'énergie. Respecter l'esprit Bikutsi avec des percussions authentiques.",
    production_tips: "Enregistrer les percussions en priorité pour établir le groove Bikutsi. Utiliser des micros de proximité pour capturer les nuances du balafon. Ajouter des effets de réverbération naturelle pour recréer l'acoustique traditionnelle.",
    created_at: new Date().toISOString()
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="text-center">
            <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-4 rounded-full w-fit mx-auto mb-4">
              <Wand2 className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Compositeur IA - Démonstration</h1>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Découvrez comment l'IA peut transformer une simple phrase d'inspiration en chanson complète. 
              Voici un exemple de création générée automatiquement.
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Inspiration Section */}
        <div className="bg-gradient-to-r from-purple-100 to-blue-100 rounded-xl p-6 mb-8">
          <div className="text-center">
            <Sparkles className="w-8 h-8 text-purple-600 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">Phrase d'inspiration</h2>
            <p className="text-lg text-purple-800 italic font-medium">
              "{demoSong.inspiration_phrase}"
            </p>
            <div className="flex justify-center items-center space-x-6 mt-4 text-sm text-gray-700">
              <span><strong>Style:</strong> {demoSong.musical_style}</span>
              <span><strong>Langue:</strong> {demoSong.language}</span>
              <span><strong>Humeur:</strong> {demoSong.mood}</span>
              <span><strong>Tempo:</strong> {demoSong.tempo}</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Chanson générée */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">{demoSong.title}</h2>
                <p className="text-gray-600">Chanson générée par l'IA en quelques secondes</p>
              </div>

              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Music className="w-5 h-5 mr-2 text-purple-600" />
                  Paroles complètes
                </h3>
                <div className="whitespace-pre-line text-sm text-gray-700 leading-relaxed max-h-96 overflow-y-auto">
                  {demoSong.lyrics}
                </div>
              </div>

              <div className="mt-6 p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-green-800 text-center">
                  ✨ <strong>Résultat impressionnant :</strong> Une chanson complète avec structure professionnelle, 
                  paroles authentiques et esprit Bikutsi respecté, générée automatiquement par l'IA !
                </p>
              </div>
            </div>
          </div>

          {/* Informations techniques */}
          <div className="space-y-6">
            {/* Structure */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Clock className="w-5 h-5 mr-2 text-blue-600" />
                Structure musicale
              </h3>
              <div className="space-y-3">
                <p className="text-sm text-gray-700">
                  <strong>Organisation :</strong> {demoSong.song_structure.structure}
                </p>
                <div className="flex flex-wrap gap-2">
                  {demoSong.song_structure.sections.map((section, index) => (
                    <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium">
                      {section}
                    </span>
                  ))}
                </div>
                <p className="text-xs text-gray-500">
                  Durée estimée: {demoSong.song_structure.estimated_duration}
                </p>
              </div>
            </div>

            {/* Accords */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Guitar className="w-5 h-5 mr-2 text-green-600" />
                Accords suggérés
              </h3>
              <div className="space-y-2">
                {demoSong.chord_suggestions.map((chord, index) => (
                  <div key={index} className="text-sm text-gray-700 bg-green-50 p-2 rounded">
                    {chord}
                  </div>
                ))}
              </div>
            </div>

            {/* Arrangement */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Volume2 className="w-5 h-5 mr-2 text-orange-600" />
                Conseils d'arrangement
              </h3>
              <p className="text-sm text-gray-700 leading-relaxed">
                {demoSong.arrangement_notes}
              </p>
            </div>

            {/* Production */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Headphones className="w-5 h-5 mr-2 text-purple-600" />
                Conseils de production
              </h3>
              <p className="text-sm text-gray-700 leading-relaxed">
                {demoSong.production_tips}
              </p>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="mt-12 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl p-8 text-center text-white">
          <Wand2 className="w-12 h-12 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-4">Créez vos propres chansons avec l'IA</h2>
          <p className="text-purple-100 mb-6 max-w-2xl mx-auto">
            Transformez vos idées en chansons complètes en quelques secondes. 
            Notre IA spécialisée en musique mondiale vous accompagne dans votre processus créatif.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a 
              href="/ai" 
              className="bg-white text-purple-600 px-8 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors inline-flex items-center justify-center"
            >
              <Sparkles className="w-5 h-5 mr-2" />
              Essayer le Compositeur IA
            </a>
            <a 
              href="/" 
              className="border border-white text-white px-8 py-3 rounded-lg font-medium hover:bg-white hover:text-purple-600 transition-colors inline-flex items-center justify-center"
            >
              <Music className="w-5 h-5 mr-2" />
              Découvrir US EXPLO
            </a>
          </div>
        </div>

        {/* Process Steps */}
        <div className="mt-12 bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">Comment ça marche ?</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="bg-purple-100 p-4 rounded-full w-fit mx-auto mb-4">
                <Sparkles className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">1. Inspiration</h3>
              <p className="text-sm text-gray-600">Saisissez une phrase qui vous inspire</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 p-4 rounded-full w-fit mx-auto mb-4">
                <Music className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">2. Style</h3>
              <p className="text-sm text-gray-600">Choisissez votre style musical préféré</p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 p-4 rounded-full w-fit mx-auto mb-4">
                <Wand2 className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">3. Génération</h3>
              <p className="text-sm text-gray-600">L'IA crée votre chanson complète</p>
            </div>
            <div className="text-center">
              <div className="bg-orange-100 p-4 rounded-full w-fit mx-auto mb-4">
                <Heart className="w-6 h-6 text-orange-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">4. Personnalisation</h3>
              <p className="text-sm text-gray-600">Sauvegardez et perfectionnez votre création</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SongDemo;