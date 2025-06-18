import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function StockDeliveryManager({ user }) {
  const [formData, setFormData] = useState({
    client_id: '',
    commodity_code: '',
    variety: '',
    quantity: ''
  });
  const [commodities, setCommodities] = useState([]);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchCommodities = async () => {
      try {
        const res = await axios.get('http://127.0.0.1:5000/commodities');
        setCommodities(res.data);
      } catch (err) {
        console.error('Error fetching commodities:', err);
      }
    };
    fetchCommodities();
  }, []);

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    try {
      await axios.post(
        'http://127.0.0.1:5000/stocks/deliver',
        formData,
        {
          headers: {
            'X-Username': user.username
          }
        }
      );
      setMessage('Stock delivered successfully');
      setFormData({ client_id: '', commodity_code: '', variety: '', quantity: '' });
    } catch (err) {
      setMessage(err.response?.data?.error || 'Error delivering stock');
    }
  };

  return (
    <div className="bg-white p-4 rounded shadow mb-4">
      <h3 className="text-lg font-semibold mb-2">Deliver Stock</h3>
      <form onSubmit={handleSubmit}>
        <input
          type="number"
          name="client_id"
          placeholder="Client ID"
          value={formData.client_id}
          onChange={handleChange}
          required
          className="border p-2 mr-2 mb-2 w-48"
        />

        <select
          name="commodity_code"
          value={formData.commodity_code}
          onChange={handleChange}
          required
          className="border p-2 mr-2 mb-2 w-48"
        >
          <option value="">Select Commodity</option>
          {commodities.map((c) => (
            <option key={c.id} value={c.commodity_code}>
              {c.name} - {c.variety}
            </option>
          ))}
        </select>

        <input
          type="text"
          name="variety"
          placeholder="Variety"
          value={formData.variety}
          onChange={handleChange}
          required
          className="border p-2 mr-2 mb-2 w-48"
        />

        <input
          type="number"
          name="quantity"
          placeholder="Quantity"
          value={formData.quantity}
          onChange={handleChange}
          required
          className="border p-2 mr-2 mb-2 w-48"
        />

        <button
          type="submit"
          className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
        >
          Deliver
        </button>
      </form>

      {message && <div className="mt-2 text-blue-600">{message}</div>}
    </div>
  );
}
