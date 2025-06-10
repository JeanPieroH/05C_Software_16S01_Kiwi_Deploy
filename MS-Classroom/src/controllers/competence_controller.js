const competenceService = require('../services/competence_service');

exports.createCompetence = async (req, res) => {
  const { name, description, id_teacher } = req.body;
  const comp = await competenceService.createCompetence(name, description, id_teacher);
  res.status(201).json(comp);
};

exports.getAllCompetences = async (req, res) => {
    const data = await competenceService.getAll();
    res.json(data);
  };
  
exports.getCompetenceById = async (req, res) => {
  const id = +req.params.id;
  const data = await competenceService.getById(id);
  if (!data) return res.status(404).json({ message: "Competence not found" });
  res.json(data);
};


exports.getCompetencesByTeacherId = async (req, res) => {
  const id_teacher = +req.params.id_teacher; 
  const competences = await competenceService.getCompetencesByTeacherId(id_teacher);
  res.json(competences);
};
  
exports.getClassroomCompetences = async (req, res) => {
  const { classroomId } = req.params;

  try {
    const competences = await competenceService.getClassroomCompetences(parseInt(classroomId));
    res.status(200).json(competences);
  } catch (error) {
    res.status(error.statusCode || 404).json({ message: error.message });
  }
};