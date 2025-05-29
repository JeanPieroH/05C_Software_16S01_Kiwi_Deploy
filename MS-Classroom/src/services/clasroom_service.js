const classroomRepo = require('../repositories/clasroom_repositoy');

exports.createClassroom = (name, description, teachers = [], students = [], competences = []) => {
  return classroomRepo.create({ name, description, teachers, students, competences });
};

exports.updateClassroom = (id, name, description, teachers = [], students = [], competences = []) => {
  return classroomRepo.update(id, { name, description, teachers, students, competences });
};
exports.getAll = () => classroomRepo.findAll();

exports.getById = (id) => classroomRepo.findById(id);

  