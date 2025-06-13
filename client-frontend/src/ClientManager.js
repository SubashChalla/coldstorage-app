import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function ClientManager() {
  const [clients, setClients] = useState([]);
  const [states, setStates] = useState([]);
  const [cities, setCities] = useState([]);
  const [manualCity, setManualCity] = useState('');
  const [formData, setFormData] = useState({
    id: null,
    client_type: '',
    first_name: '',
    last_name: '',
    org_name: '',
    s_o: '',
    address: '',
    village: '',
    mandal: '',
    district: '',
    state: '',
    city: '',
    pincode: '',
    phone: '',
    alt_phone: '',
    email: ''
  });
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchClients();
    fetchStates();
  }, []);

  useEffect(() => {
    if (formData.state) {
      fetchCities(formData.state);
    } else {
      setCities([]);
    }
  }, [formData.state]);

  useEffect(() => {
    if (formData.client_type === 'Farmer') {
      setFormData((prev) => ({
        ...prev,
        org_name: `${prev.first_name} ${prev.last_name}`.trim()
      }));
    }
  }, [formData.client_type, formData.first_name, formData.last_name]);

  const fetchClients = async () => {
    const res = await axios.get('http://127.0.0.1:5000/clients');
    setClients(res.data.clients);
  };

  const fetchStates = async () => {
    const res = await axios.get('http://127.0.0.1:5000/api/states');
    setStates(res.data.states);
  };

  const fetchCities = async (stateName) => {
    try {
      const res = await axios.get(`http://127.0.0.1:5000/api/cities?state_code=${encodeURIComponent(stateName)}`);
      setCities(res.data.cities);
    } catch {
      setCities([]);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const capitalizeWords = (str) =>
    str.replace(/\b\w+/g, (word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase());

  const formatFormData = (data) => {
    const capitalized = { ...data };
    ['first_name', 'last_name', 's_o', 'address', 'village', 'mandal', 'district', 'state', 'city', 'org_name'].forEach(
      (f) => {
        if (capitalized[f]) capitalized[f] = capitalizeWords(capitalized[f]);
      }
    );
    if (!capitalized.city && manualCity) capitalized.city = capitalizeWords(manualCity);
    return capitalized;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formatted = formatFormData(formData);
    try {
      if (formatted.id) {
        await axios.put(`http://127.0.0.1:5000/clients/${formatted.id}`, formatted);
      } else {
        await axios.post('http://127.0.0.1:5000/clients', formatted);
      }
      resetForm();
      fetchClients();
    } catch (err) {
      alert(err.response?.data?.error || 'Submission failed');
    }
  };

  const resetForm = () => {
    setFormData({
      id: null,
      client_type: '',
      first_name: '',
      last_name: '',
      org_name: '',
      s_o: '',
      address: '',
      village: '',
      mandal: '',
      district: '',
      state: '',
      city: '',
      pincode: '',
      phone: '',
      alt_phone: '',
      email: ''
    });
    setManualCity('');
  };

  const handleEdit = (client) => setFormData(client);

  const handleDelete = async (id) => {
    await axios.delete(`http://127.0.0.1:5000/clients/${id}`);
    fetchClients();
  };

  const handleSearch = async () => {
    const res = await axios.get(`http://127.0.0.1:5000/clients/search?q=${searchQuery}`);
    setClients(res.data.clients);
  };

  return (
    <div>
      <h1>Client Manager</h1>

      <div>
        <input
          type="text"
          placeholder="Search clients..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <button onClick={handleSearch}>Search</button>
      </div>

      <form onSubmit={handleSubmit}>
        <label>Client Type</label>
        <select name="client_type" value={formData.client_type} onChange={handleChange} required>
          <option value="">Select Type</option>
          <option value="Trader">Trader</option>
          <option value="Farmer">Farmer</option>
        </select>

        <input name="first_name" placeholder="First Name" value={formData.first_name} onChange={handleChange} required />
        <input name="last_name" placeholder="Last Name" value={formData.last_name} onChange={handleChange} required />
        <input
          name="org_name"
          placeholder="Organization Name"
          value={formData.org_name}
          onChange={handleChange}
          required
        />
        <input
          name="s_o"
          placeholder="S/o"
          value={formData.s_o}
          onChange={handleChange}
          disabled={formData.client_type === 'Trader'}
          required={formData.client_type === 'Farmer'}
        />

        <input name="address" placeholder="Address" value={formData.address} onChange={handleChange} />
        <input name="village" placeholder="Village" value={formData.village} onChange={handleChange} required />
        <input name="mandal" placeholder="Mandal" value={formData.mandal} onChange={handleChange} required />
        <input name="district" placeholder="District" value={formData.district} onChange={handleChange} />

        <select name="state" value={formData.state} onChange={handleChange} required>
          <option value="">Select State</option>
          {states.map((state) => (
            <option key={state} value={state}>
              {state}
            </option>
          ))}
        </select>

        {cities.length > 0 ? (
          <select name="city" value={formData.city} onChange={handleChange} required>
            <option value="">Select City</option>
            {cities.map((city) => (
              <option key={city} value={city}>
                {city}
              </option>
            ))}
          </select>
        ) : (
          <input
            name="city"
            placeholder="City/Village (Manual Entry)"
            value={manualCity}
            onChange={(e) => setManualCity(e.target.value)}
            required
          />
        )}

        <input name="pincode" placeholder="Pincode" value={formData.pincode} onChange={handleChange} />
        <input name="phone" placeholder="Phone" value={formData.phone} onChange={handleChange} required />
        <input name="alt_phone" placeholder="Alt Phone" value={formData.alt_phone} onChange={handleChange} />
        <input name="email" placeholder="Email" value={formData.email} onChange={handleChange} />

        <button type="submit">{formData.id ? 'Update' : 'Add'} Client</button>
      </form>

      <ul>
        {clients.map((client) => (
          <li key={client.id}>
            {client.first_name} {client.last_name}, {client.phone} — {client.village}, {client.mandal}
            <button onClick={() => handleEdit(client)}>Edit</button>
            <button onClick={() => handleDelete(client.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
