const express = require('express');
const classroomRoutes = require('./routes/clasroom_router');
const competenceRoutes = require('./routes/competence_router');

const app = express();
app.use(express.json());

app.use('/classrooms', classroomRoutes);
app.use('/competences', competenceRoutes);

module.exports = app;
