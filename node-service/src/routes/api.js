"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const axios_1 = __importDefault(require("axios"));
const router = (0, express_1.Router)();
const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || 'http://localhost:8000';
router.post('/select_model', (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const { model } = req.body;
        const response = yield axios_1.default.post(`${PYTHON_SERVICE_URL}/select_model`, { model });
        res.json(response.data);
    }
    catch (error) {
        res.status(500).json({ message: 'Error selecting model', error: error.message });
    }
}));
router.post('/query', (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const { prompt } = req.body;
        const response = yield axios_1.default.post(`${PYTHON_SERVICE_URL}/query`, { prompt });
        res.json(response.data);
    }
    catch (error) {
        res.status(500).json({ message: 'Error querying model', error: error.message });
    }
}));
router.get('/conversation_history', (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const response = yield axios_1.default.get(`${PYTHON_SERVICE_URL}/conversation_history`);
        res.json(response.data);
    }
    catch (error) {
        res.status(500).json({ message: 'Error retrieving conversation history', error: error.message });
    }
}));
exports.default = router;
