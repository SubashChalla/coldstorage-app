import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function StockAcceptanceManager({ user }) {
  const [formData, setFormData] = useState({
    client_id: '',
    commodity_code: '',
    variety: '',
    grade: '',
    quantity: ''
  });

  const [commodities, setCommodities] = useState([]);
  const [varieties, setVarieties] = useState([]);
  const [grades, setGrades] = useState([]);

  const [selectedCommodity, setSelectedCommodity] = useState(null);
  const [selectedVariety, setSelectedVariety] = useState(null);
  const [selectedGrade, setSelectedGrade] = useState(null);

  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/commodities/fields')
      .then(res => setCommodities(res.data))
      .catch(err => console.error('Error fetching commodities:', err));
  }, []);

  const handleCommodityChange = async (e) => {
    const commodityId = e.target.value;
    setSelectedCommodity(commodityId);
    setSelectedVariety('');
    setSelectedGrade('');
    setVarieties([]);
    setGrades([]);

    if (commodityId) {
      const res = await axios.get(`http://127.0.0.1:5000/commodities/${commodityId}/varieties`);
      setVarieties(res.data);
    }
  };

  const handleVarietyChange = async (e) => {
    const varietyId = e.target.value;
    setSelectedVariety(varietyId);
    setSelectedGrade('');
    setGrades([]);

    if (varietyId) {
      const res = await axios.get(`http://127.0.0.1:5000/varieties/${varietyId}/grades`);
      setGrades(res.data);
    }
  };

  const handleGradeChange = (e) => {
    const gradeId = e.target.value;
    setSelectedGrade(gradeId);
  };

  const handleInputChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    if (!formData.client_id || !selectedCommodity || !selectedVariety || !selectedGrade || !formData.quantity) {
      setError('All fields are required');
      return;
    }

    const selectedCommodityObj = commodities.find(c => c.id === parseInt(selectedCommodity));
    const selectedVarietyObj = varieties.find(v => v.id === parseInt(selectedVariety));
    const selectedGradeObj = grades.find(g => g.id === parseInt(selectedGrade));

    const constructedCode = `${selectedCommodityObj.name.slice(0, 3).toUpperCase()}-${selectedVarietyObj.name.slice(0, 3).toUpperCase()}`;

    try {
      await axios.post(
        'http://127.0.0.1:5000/stocks/accept',
        {
          client_id: formData.client_id,
          commodity_code: constructedCode,
          variety: selectedVarietyObj.name,
          grade: selectedGradeObj.name,
          quantity: formData.quantity
        },
        {
          headers: {
            'X-Username': user.username
          }
        }
      );
      setMessage('Stock accepted successfully');
      setFormData({ client_id: '', commodity_code: '', variety: '', grade: '', quantity: '' });
      setSelectedCommodity('');
      setSelectedVariety('');
      setSelectedGrade('');
      setVarieties([]);
      setGrades([]);
    } catch (err) {
      setError(err.response?.data?.error || 'Error accepting stock');
    }
  };

  return (
    <div className="bg-white p-4 rounded shadow mb-4">
      <h3 className="text-lg font-semibold mb-2">Accept Stock</h3>
      <form onSubmit={handleSubmit}>
        <input
          type="number"
          name="client_id"
          placeholder="Client ID"
          value={formData.client_id}
          onChange={handleInputChange}
          required
          className="border p-2 mr-2 mb-2 w-48"
        />

        <select
          value={selectedCommodity}
          onChange={handleCommodityChange}
          required
          className="border p-2 mr-2 mb-2 w-48"
        >
          <option value="">Select Commodity</option>
          {commodities.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>

        <select
          value={selectedVariety}
          onChange={handleVarietyChange}
          disabled={!varieties.length}
          required
          className="border p-2 mr-2 mb-2 w-48"
        >
          <option value="">Select Variety</option>
          {varieties.map((v) => (
            <option key={v.id} value={v.id}>{v.name}</option>
          ))}
        </select>

        <select
          value={selectedGrade}
          onChange={handleGradeChange}
          disabled={!grades.length}
          required
          className="border p-2 mr-2 mb-2 w-48"
        >
          <option value="">Select Grade</option>
          {grades.map((g) => (
            <option key={g.id} value={g.id}>{g.name}</option>
          ))}
        </select>

        <input
          type="number"
          name="quantity"
          placeholder="Quantity"
          value={formData.quantity}
          onChange={handleInputChange}
          required
          className="border p-2 mr-2 mb-2 w-48"
        />

        <button
          type="submit"
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Accept
        </button>
      </form>

      {message && <div className="mt-2 text-green-600">{message}</div>}
      {error && <div className="mt-2 text-red-600">{error}</div>}
    </div>
  );
}