const app = require('./src/app');
const { exec } = require('child_process'); // Necesario para ejecutar comandos externos
const util = require('util'); // Para usar util.promisify
const execPromise = util.promisify(exec); // Convierte exec en una función que devuelve una Promesa

const PORT = process.env.PORT || 3000;

async function runPrismaMigrations() {
  console.log("Iniciando migraciones de Prisma para Classroom...");
  try {

    const { stdout, stderr } = await execPromise('npx prisma migrate deploy');
    console.log("Migraciones de Prisma ejecutadas exitosamente.");
    if (stdout) console.log("stdout (Prisma Migrate):", stdout);
    if (stderr) console.warn("stderr (Prisma Migrate):", stderr); 
  } catch (error) {

    console.error("¡ERROR FATAL! Falló la ejecución de las migraciones de Prisma:", error.message);
    if (error.stderr) {
      console.error("Detalles del error (stderr de Prisma):", error.stderr);
    }
    process.exit(1); 
  }
}

runPrismaMigrations()
  .then(() => {
    app.listen(PORT, () => {
      console.log(`Servidor de Classrooms corriendo en http://localhost:${PORT}`);
    });
  })
  .catch((err) => {
    console.error("El servidor de Classrooms no pudo iniciarse debido a un error crítico durante las migraciones.");
  });