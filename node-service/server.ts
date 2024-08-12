import express from 'express';
import axios from 'axios';

const app = express();
const port = 3000;

app.use(express.json());

app.post('/query', async (req, res) => {
    const { model, prompt } = req.body;
    
    if (!model || !prompt) {
        return res.status(400).send({ error: 'Model and prompt are required.' });
    }

    try {
        const response = await axios.post('http://python_server:8000/query', { prompt }, {
            headers: {
                'Content-Type': 'application/json',
            },
        });
        res.send(response.data);
    } catch (error) {
        res.status(500).send({ error: error.message });
    }
});

app.post('/select_model', async (req, res) => {
    const { model } = req.body;

    if (!model) {
        return res.status(400).send({ error: 'Model is required.' });
    }

    try {
        const response = await axios.post('http://python_server:8000/select_model', { model }, {
            headers: {
                'Content-Type': 'application/json',
            },
        });
        res.send(response.data);
    } catch (error) {
        res.status(500).send({ error: error.message });
    }
});

app.get('/conversation_history', async (req, res) => {
    try {
        const response = await axios.get('http://python_server:8000/conversation_history');
        res.send(response.data);
    } catch (error) {
        res.status(500).send({ error: error.message });
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
