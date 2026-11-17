import { Bar, BarChart, XAxis, YAxis } from 'recharts'

const datos = [{ nombre: 'Ejemplo A', valor: 3 }, { nombre: 'Ejemplo B', valor: 5 }]

export default function App() {
  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold">Hackathon NFL UNAM</h1>
      <p className="text-gray-600">Plantilla lista. Reemplaza esta pantalla con tu proyecto.</p>
      <BarChart width={320} height={200} data={datos}>
        <XAxis dataKey="nombre" /><YAxis /><Bar dataKey="valor" fill="#2F7D4F" />
      </BarChart>
    </main>
  )
}
