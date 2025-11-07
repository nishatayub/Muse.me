import React from 'react';
import { motion } from 'framer-motion';

export default function FeatureCard({ feature }) {
  return (
    <motion.div
      whileHover={{ y: -8 }}
      className="bg-white p-8 rounded-lg shadow-md hover:shadow-xl transition-shadow"
    >
      <div className="text-5xl mb-4">{feature.icon}</div>
      <h3 className="text-xl font-serif font-bold text-muse-dark mb-3">
        {feature.title}
      </h3>
      <p className="text-gray-700 font-serif">
        {feature.description}
      </p>
    </motion.div>
  );
}
