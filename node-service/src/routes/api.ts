import { Router, Request, Response } from 'express';
import axios from 'axios';

const router = Router();
const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || 'http://localhost:8000';

router.post('/select_model', async (req: Request, res: Response) => {
    try {
        const { model } = req.body;
        const response = await axios.post(`${PYTHON_SERVICE_URL}/select_model`, { model });
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ message: 'Error selecting model', error: error.message });
    }
});

router.post('/query', async (req: Request, res: Response) => {
    try {
        const { prompt } = req.body;
        const response = await axios.post(`${PYTHON_SERVICE_URL}/query`, { prompt });
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ message: 'Error querying model', error: error.message });
    }
});

router.get('/conversation_history', async (req: Request, res: Response) => {
    try {
        const response = await axios.get(`${PYTHON_SERVICE_URL}/conversation_history`);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ message: 'Error retrieving conversation history', error: error.message });
    }
});

export default router;
