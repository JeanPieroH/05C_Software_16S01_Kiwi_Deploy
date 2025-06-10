const competenceRepo = require('../repositories/competence_repository');
const classroomRepo = require('../repositories/clasroom_repositoy');

exports.createCompetence = (name, description, id_teacher) => {
  return competenceRepo.create({ name, description, id_teacher });
};
exports.getAll = () => competenceRepo.findAll();

exports.getById = (id) => competenceRepo.findById(id);
exports.getCompetencesByTeacherId = (id_teacher) => {
  return competenceRepo.findByTeacherId(id_teacher);
};

exports.getCompetencesByTeacherId = (id_teacher) => {
  return competenceRepo.findByTeacherId(id_teacher);
};


exports.getClassroomCompetences = async (classroomId) => {
  if (isNaN(classroomId) || classroomId <= 0) {
    throw new ServiceError('ID de aula inválido proporcionado.', 400);
  }

  const classroom = await classroomRepo.findClassroomById(classroomId);
  if (!classroom) {
    throw new ServiceError(`Aula con ID ${classroomId} no encontrada.`, 404);
  }

  const classroomCompetences = await competenceRepo.findCompetencesByClassroomId(classroomId);

  return classroomCompetences.map(cc => ({
    id_competence: cc.competence.id,
    name: cc.competence.name,
    description: cc.competence.description,
  }));
};