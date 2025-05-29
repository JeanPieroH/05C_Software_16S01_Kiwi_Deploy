const express = require('express');
const router = express.Router();
const controller = require('../controllers/clasroom_controller');

router.post('/', controller.createClassroom);
router.patch('/:id', controller.updateClassroom);
router.get('/', controller.getAllClassrooms);
router.get('/:id', controller.getClassroomById);


module.exports = router;
