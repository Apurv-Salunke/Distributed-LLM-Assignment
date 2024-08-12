import express from 'express';
import { json } from 'body-parser';
import apiRouter from './routes/api';

const app = express();
const port = process.env.PORT || 3000;

app.use(json());
app.use('/api', apiRouter);

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
