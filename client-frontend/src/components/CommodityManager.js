import React, { useState, useEffect } from 'react';
import axios from 'axios';
import CommoditySelector from './CommoditySelector';

export default function CommodityManager({ user }) {
  const [commodities, setCommodities] = useState([]);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  // Values selected via cascading dropdowns
  const [commodityName, setCommodityName] = useState('');
  const [varietyName, setVarietyName] = useState('');
  const [gradeName, setGradeName] = useState('');
  const [hsnCode, setHsnCode] = useState('');

  const fetchCommodities = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:5000/commodities');
      setCommodities(res.data);
    } catch (err) {
      console.error('Failed to fetch commodities', err);
    }
  };

  useEffect(() => {
    fetchCommodities();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    if (!commodityName || !varietyName) {
      setError('Commodity and Variety are required');
      return;
    }

    try {
      const res = await axios.post(
        'http://127.0.0.1:5000/commodities',
        {
          name: commodityName,
          variety: varietyName,
          grade: gradeName,
          hsn_code: hsnCode,
        },
        {
          headers: {
            'X-Username': user.username,
          },
        }
      );
      setMessage(res.data.message);
      setCommodityName('');
      setVarietyName('');
      setGradeName('');
      setHsnCode('');
      fetchCommodities();
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to create commodity');
    }
  };

  return (
    <div className="bg-white p-4 shadow rounded mb-6">
      <h2 className="text-lg font-semibold mb-3">Commodity Manager</h2>

      <form onSubmit={handleSubmit} className="mb-4">
        <CommoditySelector
          onSelect={({ commodity, variety, grade }) => {
            setCommodityName(commodity?.name || '');
            setHsnCode(commodity?.hsn_code || '');
            setVarietyName(variety?.name || '');
            setGradeName(grade?.name || '');
          }}
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 mt-4"
        >
          Add Commodity
        </button>
      </form>

      {error && <p className="text-red-600 mb-2">{error}</p>}
      {message && <p className="text-green-600 mb-2">{message}</p>}

      <ul className="list-disc list-inside">
        {commodities.map((c) => (
          <li key={c.id}>
            {c.name} {c.hsn_code && `(${c.hsn_code})`}
          </li>
        ))}
      </ul>
    </div>
  );
}
