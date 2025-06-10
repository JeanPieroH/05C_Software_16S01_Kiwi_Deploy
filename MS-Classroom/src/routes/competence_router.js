const express = require('express');
const router = express.Router();
const controller = require('../controllers/competence_controller');

// El docente crea una competencia
router.post('/', controller.createCompetence);

// Obtener una competencia por id
router.get('/:id', controller.getCompetenceById);

// Obtener todas las competnecias asociadas a un docente
router.get('/teacher/:id_teacher', controller.getCompetencesByTeacherId);

router.get('/classroom/:classroomId', controller.getClassroomCompetences);

// Obtener todas las competencias
router.get('/', controller.getAllCompetences);


module.exports = router;
