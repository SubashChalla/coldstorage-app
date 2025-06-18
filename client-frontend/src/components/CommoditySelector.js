import React, { useEffect, useState } from 'react';
import axios from 'axios';

const CommoditySelector = ({ onSelect }) => {
  const [commodities, setCommodities] = useState([]);
  const [varieties, setVarieties] = useState([]);
  const [grades, setGrades] = useState([]);

  const [selectedCommodityId, setSelectedCommodityId] = useState('');
  const [selectedVarietyId, setSelectedVarietyId] = useState('');
  const [selectedGradeId, setSelectedGradeId] = useState('');

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/commodities/fields')
      .then(res => setCommodities(res.data))
      .catch(err => console.error('Error fetching commodities', err));
  }, []);

  useEffect(() => {
    if (selectedCommodityId) {
      axios.get(`http://127.0.0.1:5000/commodities/${selectedCommodityId}/varieties`)
        .then(res => setVarieties(res.data))
        .catch(err => console.error('Error fetching varieties', err));
      setSelectedVarietyId('');
      setSelectedGradeId('');
      setGrades([]);
    } else {
      setVarieties([]);
      setGrades([]);
    }
  }, [selectedCommodityId]);

  useEffect(() => {
    if (selectedVarietyId) {
      axios.get(`http://127.0.0.1:5000/varieties/${selectedVarietyId}/grades`)
        .then(res => setGrades(res.data))
        .catch(err => console.error('Error fetching grades', err));
      setSelectedGradeId('');
    } else {
      setGrades([]);
    }
  }, [selectedVarietyId]);

  useEffect(() => {
    const selectedCommodity = commodities.find(c => c.id === parseInt(selectedCommodityId));
    const selectedVariety = varieties.find(v => v.id === parseInt(selectedVarietyId));
    const selectedGrade = grades.find(g => g.id === parseInt(selectedGradeId));

    // Only call onSelect if commodity and variety are selected
    if (selectedCommodity && selectedVariety && onSelect) {
      onSelect({
        commodity: selectedCommodity,
        variety: selectedVariety,
        grade: selectedGrade || null
      });
    }
  }, [selectedCommodityId, selectedVarietyId, selectedGradeId]);

  return (
    <div className="flex flex-col gap-2 mb-4">
      <label className="font-medium">Commodity:</label>
      <select
        value={selectedCommodityId}
        onChange={e => setSelectedCommodityId(e.target.value)}
        className="border p-2 rounded"
      >
        <option value="">Select Commodity</option>
        {commodities.map(c => (
          <option key={c.id} value={c.id}>{c.name}</option>
        ))}
      </select>

      <label className="font-medium">Variety:</label>
      <select
        value={selectedVarietyId}
        onChange={e => setSelectedVarietyId(e.target.value)}
        disabled={!varieties.length}
        className="border p-2 rounded"
      >
        <option value="">Select Variety</option>
        {varieties.map(v => (
          <option key={v.id} value={v.id}>{v.name}</option>
        ))}
      </select>

      <label className="font-medium">Grade (optional):</label>
      <select
        value={selectedGradeId}
        onChange={e => setSelectedGradeId(e.target.value)}
        disabled={!grades.length}
        className="border p-2 rounded"
      >
        <option value="">Select Grade</option>
        {grades.map(g => (
          <option key={g.id} value={g.id}>{g.name}</option>
        ))}
      </select>
    </div>
  );
};

export default CommoditySelector;
