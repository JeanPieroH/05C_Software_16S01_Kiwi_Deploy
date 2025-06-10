const classroomService = require('../services/clasroom_service');

exports.createClassroom = async (req, res) => {
  const { name, description, teachers, students, competences } = req.body;
  
  try{
    const classroom = await classroomService.createClassroom(name, description,teachers, students, competences);
    res.status(201).json(classroom);
  } catch (error) {
    console.error("Error creating classroom:", error);
    res.status(500).json({ error: "Internal server error", details: error.message });
  }
};
//-----------------------
exports.addStudentsByIdsToClassroom = async (req, res) => {
  const { classroomId } = req.params;
  const { students_id } = req.body;

  try {
    const addedStudentsCount = await classroomService.addStudentsByIdsToClassroom(parseInt(classroomId), students_id);
    res.status(201).json({ message: "Students successfully added to classroom.", data: { count: addedStudentsCount } });
  } catch (error) {
    res.status(error.statusCode || 400).json({ message: error.message });
  }
};
//-----------------------
exports.addTeachersByIdsToClassroom = async (req, res) => {
  const { classroomId } = req.params;
  const { teachers_id } = req.body;

  try {
    const addedTeachersCount = await classroomService.addTeachersByIdsToClassroom(parseInt(classroomId), teachers_id);
    res.status(201).json({ message: "Teachers successfully added to classroom.", data: { count: addedTeachersCount } });
  } catch (error) {
    res.status(error.statusCode || 400).json({ message: error.message });
  }
};
//--------------------------------------
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
  const { id } = req.params;
  try {
    const classroom = await classroomService.getById(parseInt(id));
    res.status(200).json(classroom);
  } catch (error) {
    res.status(error.statusCode || 404).json({ message: error.message });
  }
};

exports.getClassroomsByTeacherId = async (req, res) => {
  const id_teacher = +req.params.id_teacher; // Convertir a número si es necesario
  const classrooms = await classroomService.getClassroomsByTeacherId(id_teacher);
  res.json(classrooms);
};

exports.getClassroomsByUserId = async (req, res) => {
  const { userId } = req.params;

  try {
    const classrooms = await classroomService.getClassroomsByUserId(parseInt(userId));
    res.status(200).json(classrooms);
  } catch (error) {
    res.status(error.statusCode || 404).json({ message: error.message });
  }
};
//------------------------------------
exports.getTeachersByClassroomId = async (req, res) => {
  const { classroomId } = req.params;

  try {
    const teacherIds = await classroomService.getTeachersByClassroomId(parseInt(classroomId));
    res.status(200).json({ teachers_id: teacherIds });
  } catch (error) {
    res.status(error.statusCode || 400).json({ message: error.message });
  }
};

exports.getStudentsByClassroomId = async (req, res) => {
  const { classroomId } = req.params;

  try {
    const studentIds = await classroomService.getStudentsByClassroomId(parseInt(classroomId));
    res.status(200).json({ students_id: studentIds });
  } catch (error) {
    res.status(error.statusCode || 400).json({ message: error.message });
  }
};
//-------------------------
exports.getCompetencesForClassroom = async (req, res) => {
  const id = +req.params.id; // ID del Classroom
  const competences = await classroomService.getCompetencesByClassroomId(id);
  
  if (competences === null) { // Si el classroom no fue encontrado
    return res.status(404).json({ message: "Classroom not found" });
  }
  res.json(competences);
};


exports.associateCompetencesToClassroomWithPoints = async (req, res) => {
  const { classroomId } = req.params;
  const { competences_id } = req.body;

  try {
    const addedCompetencesCount = await classroomService.associateCompetencesToClassroomWithPoints(parseInt(classroomId), competences_id);
    res.status(201).json({ message: "Competencias asociadas al aula exitosamente y puntos inicializados.", data: { count: addedCompetencesCount } });
  } catch (error) {
    res.status(error.statusCode || 400).json({ message: error.message });
  }
};

//----------------------

exports.processQuizCompetenceAndClassroomPoints = async (req, res) => {
  const { classroomId } = req.params;
  const quizData = req.body;

  try {
    const result = await classroomService.processQuizCompetenceAndClassroomPoints(parseInt(classroomId), quizData);
    res.status(200).json({ message: "Quiz, asociaciones y puntos del aula actualizados exitosamente.", data: result });
  } catch (error) {
    res.status(error.statusCode || 400).json({ message: error.message });
  }
};

exports.removeQuizzesFromClassroom = async (req, res) => {
  const { classroomId } = req.params;
  const { quiz_id } = req.body;

  try {
    const updatedClassroom = await classroomService.removeQuizzesFromClassroom(parseInt(classroomId), quiz_id);
    res.status(200).json({ message: "Quizzes eliminados del aula exitosamente.", data: updatedClassroom });
  } catch (error) {
    res.status(error.statusCode || 400).json({ message: error.message });
  }
};

//-----------------------
exports.recordStudentQuizPoints = async (req, res) => {
  const { classroomId } = req.params;
  const studentQuizData = req.body;

  try {
    const result = await classroomService.recordStudentQuizPoints(
      parseInt(classroomId),
      studentQuizData
    );
    res.status(200).json({
      message: 'Puntos de estudiante y competencias actualizados exitosamente.',
      data: result,
    });
  } catch (error) {
    res.status(error.statusCode || 400).json({ message: error.message });
  }
};

//-------------------------------------
exports.getStudentRanking = async (req, res) => {
  const { classroomId } = req.params;

  try {
    const ranking = await classroomService.getStudentRanking(parseInt(classroomId));
    res.status(200).json(ranking);
  } catch (error) {
    res.status(error.statusCode || 404).json({ message: error.message });
  }
};


exports.getStudentCompetenceRanking = async (req, res) => {
  const { classroomId, competenceId } = req.params;

  try {
    const ranking = await classroomService.getStudentCompetenceRanking(parseInt(classroomId), parseInt(competenceId));
    res.status(200).json(ranking);
  } catch (error) {
    res.status(error.statusCode || 404).json({ message: error.message });
  }
};