const repo = require('../repositories/competence_repository');

exports.createCompetence = (name, description, id_teacher) => {
  return repo.create({ name, description, id_teacher });
};
exports.getAll = () => repo.findAll();

exports.getById = (id) => repo.findById(id);
