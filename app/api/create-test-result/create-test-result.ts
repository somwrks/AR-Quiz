import axios from 'axios';

export default async function handler(req:any, res:any) {
    const response = await axios.post('http://localhost:5000/api/create-test-result', req.body);
    res.status(response.status).json(response.data);
}