const classroomRepo = require('../repositories/clasroom_repositoy');
const competenceRepo = require('../repositories/competence_repository'); 

class ServiceError extends Error {
  constructor(message, statusCode = 400) {
    super(message);
    this.name = 'ServiceError';
    this.statusCode = statusCode;
  }
}

exports.createClassroom = (name, description, teachers = []) => {
  return classroomRepo.create({ name, description, teachers });
};

//-------------------------------------
exports.addStudentsByIdsToClassroom = async (classroomId, studentIds) => {
  if (isNaN(classroomId) || classroomId <= 0) throw new ServiceError("Invalid classroom ID provided.", 400);
  //if (!Array.isArray(studentIds) || studentIds.length === 0) throw new ServiceError("Invalid input: 'students_id' array is required and must not be empty.", 400);

  const classroom = await classroomRepo.findClassroomById(classroomId);
  if (!classroom) throw new ServiceError(`Classroom with ID ${classroomId} not found.`, 404);

  const studentsToCreate = [];
  for (const studentId of studentIds) {
    if (typeof studentId !== 'number' || !Number.isInteger(studentId) || studentId <= 0) continue;
    const isAlreadyIn = await classroomRepo.isStudentInClassroom(studentId, classroomId);
    if (!isAlreadyIn) {
      studentsToCreate.push({ id_student: studentId, id_classroom: classroomId, role_classroom: "STUDENT" ,obtained_points:0});
    }
  }

  if (studentsToCreate.length === 0) return 0;

  const result = await classroomRepo.addMultipleStudentsToClassroom(studentsToCreate);
  return result.count;
};
//-------------------------------------
exports.addTeachersByIdsToClassroom = async (classroomId, teacherIds) => {
  if (isNaN(classroomId) || classroomId <= 0) throw new ServiceError("Invalid classroom ID provided.", 400);
  //if (!Array.isArray(teacherIds) || teacherIds.length === 0) throw new ServiceError("Invalid input: 'teachers_id' array is required and must not be empty.", 400);

  const classroom = await classroomRepo.findClassroomById(classroomId);
  if (!classroom) throw new ServiceError(`Classroom with ID ${classroomId} not found.`, 404);

  const teachersToCreate = [];
  for (const teacherId of teacherIds) {
    if (typeof teacherId !== 'number' || !Number.isInteger(teacherId) || teacherId <= 0) continue;
    const isAlreadyIn = await classroomRepo.isTeacherInClassroom(teacherId, classroomId);
    if (!isAlreadyIn) {
      teachersToCreate.push({ id_teacher: teacherId, id_classroom: classroomId, role_classroom: "EDITOR" });
    }
  }

  if (teachersToCreate.length === 0) return 0;

  const result = await classroomRepo.addMultipleTeachersToClassroom(teachersToCreate);
  return result.count;
};
//---------------------------------------


exports.updateClassroom = (id, name, description, teachers = [], students = [], competences = []) => {
  return classroomRepo.update(id, { name, description, teachers, students, competences });
};
exports.getAll = () => classroomRepo.findAll();

exports.getById = async (id) => {
  if (isNaN(id) || id <= 0) throw new ServiceError("ID de aula inválido proporcionado.", 400);

  const classroom = await classroomRepo.findById(id);
  if (!classroom) throw new ServiceError(`Aula con ID ${id} no encontrada.`, 404);
  const formattedCompetences = classroom.competences.map(({ competence }) => competence);
  return {
    id: classroom.id,
    name: classroom.name,
    description: classroom.description,
    quiz: classroom.quiz,
    competences: formattedCompetences
  };
};

exports.getClassroomsByTeacherId = async (teacherId) => {
  if (isNaN(teacherId) || teacherId <= 0) {
    throw new ServiceError('ID de docente inválido proporcionado.', 400);
  }

  const classroomTeachers = await classroomRepo.findClassroomsByTeacherId(teacherId);

  

  return classroomTeachers.map(ct => ({
    id: ct.classroom.id,
    name: ct.classroom.name,
    description: ct.classroom.description,
  }));
};

// -------------------------------
exports.getClassroomsByUserId = async (userId) => {
  if (isNaN(userId) || userId <= 0) {
    throw new ServiceError('ID de usuario inválido proporcionado.', 400);
  }

  const studentClassrooms = await classroomRepo.findClassroomsByStudentId(userId);
  const teacherClassrooms = await classroomRepo.findClassroomsByTeacherId(userId);

  const combinedClassrooms = {};

  studentClassrooms.forEach(cs => {
    combinedClassrooms[cs.classroom.id] = {
      id: cs.classroom.id,
      name: cs.classroom.name,
      description: cs.classroom.description,
    };
  });

  teacherClassrooms.forEach(ct => {
    combinedClassrooms[ct.classroom.id] = {
      id: ct.classroom.id,
      name: ct.classroom.name,
      description: ct.classroom.description,
    };
  });

  const uniqueClassrooms = Object.values(combinedClassrooms);

  if (uniqueClassrooms.length === 0) {
    throw new ServiceError(`No se encontraron aulas para el usuario con ID ${userId}.`, 404);
  }

  return uniqueClassrooms;
};

exports.findClassroomWithCompetencesById = async (id) => {
  return await prisma.Classroom.findUnique({
    where: { id },
    select: {
      id: true,
      name: true,
      description: true,
      classroomCompetencies: { // Accede a la tabla de unión
        select: {
          competence: { // Selecciona la competencia real a través de la relación
            select: {
              id: true,
              name: true,
              description: true
            }
          }
        }
      }
    }
  });
};


exports.getTeachersByClassroomId = async (classroomId) => {
  if (isNaN(classroomId) || classroomId <= 0) throw new ServiceError("Invalid classroom ID provided.", 400);

  const classroom = await classroomRepo.findClassroomById(classroomId);
  if (!classroom) throw new ServiceError(`Classroom with ID ${classroomId} not found.`, 404);

  const teacherIds = await classroomRepo.findTeachersByClassroomId(classroomId);
  return teacherIds;
};

exports.getStudentsByClassroomId = async (classroomId) => {
  if (isNaN(classroomId) || classroomId <= 0) throw new ServiceError("Invalid classroom ID provided.", 400);

  const classroom = await classroomRepo.findClassroomById(classroomId);
  if (!classroom) throw new ServiceError(`Classroom with ID ${classroomId} not found.`, 404);

  const studentIds = await classroomRepo.findStudentsByClassroomId(classroomId);
  return studentIds;
};

exports.getCompetencesByClassroomId = async (classroomId) => {
  return classroomRepo.getCompetencesByClassroomId(classroomId);
};

//----------------------------
exports.associateCompetencesToClassroomWithPoints = async (classroomId, competenceIds) => {
  if (isNaN(classroomId) || classroomId <= 0) throw new ServiceError("ID de aula inválido proporcionado.", 400);
  if (!Array.isArray(competenceIds) || competenceIds.length === 0) throw new ServiceError("Entrada inválida: 'competences_id' es un arreglo requerido y no debe estar vacío.", 400);

  const classroom = await classroomRepo.findClassroomById(classroomId);
  if (!classroom) throw new ServiceError(`Aula con ID ${classroomId} no encontrada.`, 404);

  const existingCompetences = await classroomRepo.findCompetencesByIds(competenceIds);
  const validCompetenceIds = new Set(existingCompetences.map(c => c.id));
  const missingCompetences = competenceIds.filter(id => !validCompetenceIds.has(id));

  if (missingCompetences.length > 0) {
    throw new ServiceError(`Las siguientes competencias no existen: ${missingCompetences.join(', ')}.`, 404);
  }

  const competencesToCreate = [];
  for (const competenceId of competenceIds) {
    if (typeof competenceId !== 'number' || !Number.isInteger(competenceId) || competenceId <= 0) continue;
    const isAlreadyAssociated = await classroomRepo.isCompetenceInClassroom(competenceId, classroomId);
    if (!isAlreadyAssociated) {
      competencesToCreate.push({ id_competence: competenceId, id_classroom: classroomId, total_points: 0 });
    }
  }

  if (competencesToCreate.length === 0) return 0;

  const result = await classroomRepo.addMultipleCompetencesToClassroom(competencesToCreate);
  return result.count;
};

//----------------------------
exports.processQuizCompetenceAndClassroomPoints = async (classroomId, quizData) => {
  // Validaciones de entrada
  if (isNaN(classroomId) || classroomId <= 0) {
    throw new ServiceError("ID de aula inválido proporcionado.", 400);
  }
  if (!quizData || typeof quizData !== 'object') {
    throw new ServiceError("Entrada inválida: Los datos del quiz son requeridos.", 400);
  }

  const { quiz_id, total_points, questions } = quizData;

  if (isNaN(quiz_id) || quiz_id <= 0) {
    throw new ServiceError("El 'quiz_id' es inválido o no proporcionado.", 400);
  }
  if (typeof total_points !== 'number' || total_points < 0) {
    throw new ServiceError("El 'total_points' del quiz debe ser un número válido y no negativo.", 400);
  }
  if (!Array.isArray(questions)) {
    throw new ServiceError("La propiedad 'questions' debe ser un arreglo.", 400);
  }

  // Verificar existencia del aula
  const classroom = await classroomRepo.findById(classroomId);
  if (!classroom) {
    throw new ServiceError(`Aula con ID ${classroomId} no encontrada.`, 404);
  }

  const quizIdsToUpdateClassroom = new Set(classroom.quiz);
  quizIdsToUpdateClassroom.add(quiz_id);

  const competenceQuestionAssociations = [];
  const allCompetenceIds = new Set();
  const competencePointsToUpdate = {}; // { competenceId: totalPoints }

  for (const question of questions) {
    if (!question.question_id || typeof question.question_id !== 'number' || question.question_id <= 0) {
      throw new ServiceError("Cada pregunta debe tener un 'question_id' válido y positivo.", 400);
    }
    if (typeof question.points !== 'number' || question.points < 0) {
      throw new ServiceError("Cada pregunta debe tener un 'points' válido y no negativo.", 400);
    }
    if (!Array.isArray(question.competences_id) || question.competences_id.length === 0) {
      throw new ServiceError("Cada pregunta debe tener un arreglo 'competences_id' no vacío.", 400);
    }

    for (const compId of question.competences_id) {
      if (typeof compId !== 'number' || compId <= 0) continue; // Ignorar IDs de competencia inválidos
      
      competenceQuestionAssociations.push({
        id_question: question.question_id,
        id_competence: compId,
      });
      allCompetenceIds.add(compId);

      if (!competencePointsToUpdate[compId]) {
        competencePointsToUpdate[compId] = 0;
      }
      competencePointsToUpdate[compId] += question.points;
    }
  }

  // Validar que todas las competencias referenciadas existen
  const existingCompetences = await competenceRepo.findCompetencesByIds(Array.from(allCompetenceIds));
  const existingCompetenceIds = new Set(existingCompetences.map(c => c.id));
  const missingCompetences = Array.from(allCompetenceIds).filter(id => !existingCompetenceIds.has(id));

  if (missingCompetences.length > 0) {
    throw new ServiceError(`Las siguientes competencias no existen: ${missingCompetences.join(', ')}.`, 404);
  }

  // Actualizar la lista de quizzes y los puntos totales del aula
  const updatedClassroom = await classroomRepo.updateQuizListAndTotalPoints(classroomId, Array.from(quizIdsToUpdateClassroom), total_points);
  
  // Añadir o actualizar asociaciones de preguntas y competencias
  const resultAssociations = await competenceRepo.addMultipleCompetenceQuestions(competenceQuestionAssociations);

  // Actualizar los puntos totales de las competencias en Classroom_Competence
  let updatedCompetencePointsCount = 0;
  for (const compId in competencePointsToUpdate) {
    await competenceRepo.upsertTotalPoints(classroomId, parseInt(compId), competencePointsToUpdate[compId]);
    updatedCompetencePointsCount++;
  }

  return {
    classroom: updatedClassroom,
    competence_question_associations_count: resultAssociations.count,
    classroom_competence_points_updated_count: updatedCompetencePointsCount,
  };
};

//----------------------------
exports.removeQuizzesFromClassroom = async (classroomId, quizIdsToRemove) => {
  if (isNaN(classroomId) || classroomId <= 0) {
    throw new ServiceError("ID de aula inválido proporcionado.", 400);
  }
  if (!Array.isArray(quizIdsToRemove) || quizIdsToRemove.length === 0) {
    throw new ServiceError("Entrada inválida: 'quiz_id' es un arreglo requerido y no debe estar vacío.", 400);
  }

  const classroom = await classroomRepo.findById(classroomId);
  if (!classroom) {
    throw new ServiceError(`Aula con ID ${classroomId} no encontrada.`, 404);
  }

  const currentQuizIds = new Set(classroom.quiz);
  let hasChanges = false;
  
  for (const quizId of quizIdsToRemove) {
    if (typeof quizId !== 'number' || !Number.isInteger(quizId) || quizId <= 0) {
      continue;
    }
    if (currentQuizIds.has(quizId)) {
      currentQuizIds.delete(quizId);
      hasChanges = true;
    }
  }

  if (!hasChanges) {
      return classroom; 
  }
  
  const updatedQuizList = Array.from(currentQuizIds);
  const updatedClassroom = await classroomRepo.updateQuizList(classroomId, updatedQuizList);
  
  return updatedClassroom;
};



//--------------------------------
exports.recordStudentQuizPoints = async (classroomId, studentQuizData) => {
  // Validaciones de entrada del request
  if (isNaN(classroomId) || classroomId <= 0) {
    throw new ServiceError('ID de aula inválido proporcionado.', 400);
  }
  if (!studentQuizData || typeof studentQuizData !== 'object') {
    throw new ServiceError('Datos del estudiante del quiz son requeridos.', 400);
  }

  const { student_id, obtained_points, question_student } = studentQuizData;

  if (isNaN(student_id) || student_id <= 0) {
    throw new ServiceError('El student_id es inválido o no proporcionado.', 400);
  }
  if (typeof obtained_points !== 'number' || obtained_points < 0) {
    throw new ServiceError('Los obtained_points del quiz deben ser un número válido y no negativo.', 400);
  }
  if (!Array.isArray(question_student) || question_student.length === 0) {
    throw new ServiceError('La lista de preguntas del estudiante es requerida y no debe estar vacía.', 400);
  }

  // Verificar existencia del aula
  const classroom = await classroomRepo.findById(classroomId);
  if (!classroom) {
    throw new ServiceError(`Aula con ID ${classroomId} no encontrada.`, 404);
  }

  // Upsert o crear el registro en Classroom_Student y actualizar sus puntos totales obtenidos para el aula
  await classroomRepo.upsertStudentPoints(student_id, classroomId, obtained_points);

  const competencePointsAccumulator = {}; // { competenceId: totalPointsObtainedForThisCompetence }
  const processedCompetenceIds = new Set();

  for (const qStudent of question_student) {
    if (isNaN(qStudent.question_id) || qStudent.question_id <= 0) {
      throw new ServiceError('Cada pregunta debe tener un question_id válido y positivo.', 400);
    }
    if (typeof qStudent.obtained_points !== 'number' || qStudent.obtained_points < 0) {
      throw new ServiceError('Los puntos obtenidos para cada pregunta deben ser un número válido y no negativo.', 400);
    }

    const competenceIdsForQuestion = await competenceRepo.findCompetenceIdsByQuestionId(qStudent.question_id);

    for (const compId of competenceIdsForQuestion) {
      if (!competencePointsAccumulator[compId]) {
        competencePointsAccumulator[compId] = 0;
      }
      competencePointsAccumulator[compId] += qStudent.obtained_points;
      processedCompetenceIds.add(compId);
    }
    
  }

  // Validar que todas las competencias acumuladas existen
  const existingCompetences = await competenceRepo.findCompetencesByIds(Array.from(processedCompetenceIds));

  const validCompetenceIds = new Set(existingCompetences.map(c => c.id));
  const missingCompetences = Array.from(processedCompetenceIds).filter(id => !validCompetenceIds.has(id));

  if (missingCompetences.length > 0) {
    throw new ServiceError(`Las siguientes competencias referenciadas no existen: ${missingCompetences.join(', ')}.`, 404);
  }

  const updatedCompetencesSummary = [];
  for (const compId in competencePointsAccumulator) {
    const points = competencePointsAccumulator[compId];
    await competenceRepo.upsertStudentCompetencePoints(
      student_id,
      parseInt(compId),
      classroomId,
      points
    );
    updatedCompetencesSummary.push({
      competence_id: parseInt(compId),
      points_added: points,
    });
  }

  return {
    classroom_id: classroomId,
    student_id: student_id,
    classroom_student_points_updated: true,
    updated_competences: updatedCompetencesSummary,
  };
};


exports.getStudentRanking = async (classroomId) => {
  if (isNaN(classroomId) || classroomId <= 0) {
    throw new ServiceError('ID de aula inválido proporcionado.', 400);
  }

  const classroom = await classroomRepo.findClassroomById(classroomId);
  if (!classroom) {
    throw new ServiceError(`Aula con ID ${classroomId} no encontrada.`, 404);
  }

  const students = await classroomRepo.findStudentsByClassroomIdOrderedByPoints(classroomId);

  if (students.length === 0) {
    throw new ServiceError(`No se encontraron estudiantes para el ranking en el aula con ID ${classroomId}.`, 404);
  }

  return students.map((student, index) => ({
    ranking: index + 1,
    obtained_points: student.obtained_points,
    student: student.id_student,
  }));
};


exports.getStudentCompetenceRanking = async (classroomId, competenceId) => {
  if (isNaN(classroomId) || classroomId <= 0) {
    throw new ServiceError('ID de aula inválido proporcionado.', 400);
  }
  if (isNaN(competenceId) || competenceId <= 0) {
    throw new ServiceError('ID de competencia inválido proporcionado.', 400);
  }

  const classroom = await classroomRepo.findClassroomById(classroomId);
  if (!classroom) {
    throw new ServiceError(`Aula con ID ${classroomId} no encontrada.`, 404);
  }

  const competence = await competenceRepo.findCompetenceById(competenceId);
  if (!competence) {
    throw new ServiceError(`Competencia con ID ${competenceId} no encontrada.`, 404);
  }

  const students = await classroomRepo.findStudentsByClassroomAndCompetenceIdOrderedByPoints(classroomId, competenceId);

  if (students.length === 0) {
    throw new ServiceError(`No se encontraron estudiantes con puntos registrados para la competencia ${competenceId} en el aula ${classroomId}.`, 404);
  }

  return students.map((student, index) => ({
    ranking: index + 1,
    obtained_points: student.obtained_points,
    student: student.id_student,
  }));
};