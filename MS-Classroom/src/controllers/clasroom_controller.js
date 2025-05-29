const classroomService = require('../services/clasroom_service');

exports.createClassroom = async (req, res) => {
  const { name, description, teachers, students, competences } = req.body;
  const classroom = await classroomService.createClassroom(name, description, teachers, students, competences);
  res.status(201).json(classroom);
};

exports.updateClassroom = async (req, res) => {
  const { id } = req.params;
  const { name, description, teachers, students, competences } = req.body;
  const updated = await classroomService.updateClassroom(+id, name, description, teachers, students, competences);
  res.json(updated);
};

exports.getAllClassrooms = async (req, res) => {
    const data = await classroomService.getAll();
    res.json(data);
};
  
exports.getClassroomById = async (req, res) => {
    const id = +req.params.id;
    const data = await classroomService.getById(id);
    if (!data) return res.status(404).json({ message: "Classroom not found" });
    res.json(data);
};
  