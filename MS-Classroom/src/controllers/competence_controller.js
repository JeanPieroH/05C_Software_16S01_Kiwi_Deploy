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
  