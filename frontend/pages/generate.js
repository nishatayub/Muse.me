import React, { useState } from 'react';
import Head from 'next/head';
import { motion } from 'framer-motion';
import axios from 'axios';
import PersonaCard from '../components/PersonaCard';
import LoadingSpinner from '../components/LoadingSpinner';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Generate() {
  const [input, setInput] = useState('');
  const [aestheticPreference, setAestheticPreference] = useState('');
  const [loading, setLoading] = useState(false);
  const [persona, setPersona] = useState(null);
  const [error, setError] = useState(null);

  const aesthetics = [
    '✨ Cyberpunk Poet',
    '🌾 Cottagecore Romantic',
    '☁️ Cloudcore Dreamer',
    '📚 Dark Academia',
    '🎨 Maximalist Creator',
    '🌙 No Preference'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!input.trim()) {
      setError('Please describe yourself or your daily routine');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/generate`, {
        user_input: input,
        aesthetic_preference: aestheticPreference && aestheticPreference !== '🌙 No Preference' ? aestheticPreference : null
      });

      setPersona(response.data);
    } catch (err) {
      console.error('Error generating persona:', err);
      setError(
        err.response?.data?.detail || 
        'Failed to generate persona. Please try again with a different input.'
      );
    } finally {
      setLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
  };

  return (
    <>
      <Head>
        <title>Generate Your Aesthetic Alter Ego | Muse.me</title>
        <meta name="description" content="Transform your life into an aesthetic alter ego" />
      </Head>

      <main className="min-h-screen bg-gradient-to-b from-muse-cream to-white py-12 px-4">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="max-w-3xl mx-auto"
        >
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-5xl font-serif font-bold text-muse-dark mb-4">
              ✨ Create Your Aesthetic Alter Ego ✨
            </h1>
            <p className="text-lg text-gray-700 font-serif">
              Describe your daily life, and we'll romanticize it into something extraordinary
            </p>
          </div>

          {!persona ? (
            // Form Section
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-xl shadow-lg p-8 mb-8"
            >
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Main Input */}
                <div>
                  <label className="block text-lg font-serif font-bold text-muse-dark mb-3">
                    Tell us about yourself
                  </label>
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Write about your daily routine, hobbies, personality, or any aspect of your life you'd like to romanticize..."
                    className="w-full h-40 p-4 border-2 border-muse-rose rounded-lg font-serif text-gray-800 placeholder-gray-400 focus:outline-none focus:border-muse-dark transition-colors resize-none"
                  />
                  <p className="text-sm text-gray-500 mt-2">Minimum 10 characters. Be descriptive for best results.</p>
                </div>

                {/* Aesthetic Preference */}
                <div>
                  <label className="block text-lg font-serif font-bold text-muse-dark mb-3">
                    Aesthetic Preference (Optional)
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {aesthetics.map((aesthetic) => (
                      <motion.button
                        key={aesthetic}
                        type="button"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setAestheticPreference(aesthetic)}
                        className={`py-3 px-4 rounded-lg font-serif font-bold transition-all ${
                          aestheticPreference === aesthetic
                            ? 'bg-muse-rose text-white shadow-lg'
                            : 'bg-gray-100 text-muse-dark hover:bg-gray-200'
                        }`}
                      >
                        {aesthetic}
                      </motion.button>
                    ))}
                  </div>
                </div>

                {/* Error Message */}
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-red-50 border-l-4 border-red-500 p-4 rounded"
                  >
                    <p className="text-red-700 font-serif">{error}</p>
                  </motion.div>
                )}

                {/* Submit Button */}
                <motion.button
                  type="submit"
                  disabled={loading}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full py-4 bg-muse-rose text-white rounded-lg font-serif text-lg font-bold hover:shadow-lg transition-shadow disabled:opacity-50"
                >
                  {loading ? 'Generating Your Persona...' : '✨ Generate My Aesthetic Alter Ego ✨'}
                </motion.button>
              </form>
            </motion.div>
          ) : (
            // Results Section
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6 }}
            >
              <PersonaCard persona={persona} />

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="flex gap-4 justify-center mt-8"
              >
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => {
                    setPersona(null);
                    setInput('');
                    setAestheticPreference('');
                    setError(null);
                  }}
                  className="px-8 py-3 bg-muse-rose text-white rounded-full font-serif font-bold hover:shadow-lg transition-shadow"
                >
                  ✨ Create Another
                </motion.button>
              </motion.div>
            </motion.div>
          )}

          {/* Loading Spinner */}
          {loading && <LoadingSpinner />}
        </motion.div>
      </main>
    </>
  );
}
