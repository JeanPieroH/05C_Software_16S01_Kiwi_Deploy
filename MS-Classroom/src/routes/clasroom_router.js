const express = require('express');
const router = express.Router();
const controller = require('../controllers/clasroom_controller');

// Un docente crea una clase
router.post('/', controller.createClassroom);
// Añade estudiantes por id a un classroom y teachers a un classroom, asignando roles
router.post('/:classroomId/add-students', controller.addStudentsByIdsToClassroom);
router.post('/:classroomId/add-teachers', controller.addTeachersByIdsToClassroom);


// Obtener los id de los teacher y students de un classrroom
router.get('/:classroomId/teachers', controller.getTeachersByClassroomId);
router.get('/:classroomId/students', controller.getStudentsByClassroomId);


// Obtiene la informacion de un classroom por id (atibutos primarios , las competencias(atibutos primarios y derivados)y los quices(atributos primarios))
router.get('/:id', controller.getClassroomById);

// Obtiene todos los classrroom(atibutos primarios)
router.get('/teacher/:id_teacher', controller.getClassroomsByTeacherId);


router.get('/user/:userId', controller.getClassroomsByUserId);


// Obtener todas las competencias asociadas a un classroom
router.get('/:id/competences', controller.getCompetencesForClassroom);

// Asocia una lista de competencias identificadas por el id a una classroom
router.post('/:classroomId/competences/associate', controller.associateCompetencesToClassroomWithPoints);



router.patch('/:id', controller.updateClassroom);

// Añadir los quizes (incluye question y sus competencias asociadas, actualizando el total points) al classroom
router.patch('/:classroomId/quizzes-competences', controller.processQuizCompetenceAndClassroomPoints);


// Añadir los resultados de un quiz rendido por un estudiante
router.patch('/:classroomId/student-quiz-points', controller.recordStudentQuizPoints);


// Eliminar los id de quizes de un classroom
router.delete('/:classroomId/quizzes', controller.removeQuizzesFromClassroom);


// Para verificar, obtiene toda la informacion de los classroom
router.get('/', controller.getAllClassrooms);



router.get('/:classroomId/ranking', controller.getStudentRanking);

router.get('/:classroomId/competences/:competenceId/ranking', controller.getStudentCompetenceRanking);

module.exports = router;
