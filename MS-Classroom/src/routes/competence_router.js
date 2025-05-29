const express = require('express');
const router = express.Router();
const controller = require('../controllers/competence_controller');

router.post('/', controller.createCompetence);
router.get('/', controller.getAllCompetences);
router.get('/:id', controller.getCompetenceById);

module.exports = router;
