import { useEffect, useState } from 'react'
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button';

interface Launch {
  flight_number: number;
  name: string;
  date_utc: string;
  success: boolean;
}
// interface Error { message: string | null }
function App() {
  const [launches, setLaunches] = useState<Launch[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(0);
  const rowsPerPage = 5;

  useEffect(() => {
    const fetchLaunches = async () => {
      try {
        const response = await fetch('https://api.spacexdata.com/v4/launches');
        const data = await response.json();
        setLaunches(data);
      } catch (error) {
        if (error instanceof Error) {
          setError(error.message);
        }
        setError('Failed to fetch launches');
      }
    };

    fetchLaunches();
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const handleNextPage = () => {
    if ((currentPage + 1) * rowsPerPage < launches.length) {
      setCurrentPage(currentPage + 1);
    }
  };

  const handlePreviousPage = () => {
    if (currentPage > 0) {
      setCurrentPage(currentPage - 1);
    }
  };

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
    <h1 className="text-4xl font-bold justify-center mb-4">SpaceX Launches</h1>
    {error && <p className="text-red-500">{error}</p>}
    <Table className="border border-gray-300 shadow-lg">
      <TableHeader>
        <TableRow>
          <TableHead >Name</TableHead>
          <TableHead>Date</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {launches
          .slice(currentPage * rowsPerPage, (currentPage + 1) * rowsPerPage)
          .map((launch) => (
            <TableRow key={launch.flight_number} className="hover:bg-gray-50">
              <TableCell className="p-2">{launch.name}</TableCell>
              <TableCell className="p-2">{formatDate(launch.date_utc)}</TableCell>
              <TableCell className={`p-2 font-bold ${launch.success ? 'text-green-600' : 'text-red-600'}`}>
                {launch.success ? 'Success' : 'Failure'}
              </TableCell>
            </TableRow>
          ))}
      </TableBody>
    </Table>
    <div className="flex justify-between mt-4">
      <Button
        onClick={handlePreviousPage}
        disabled={currentPage === 0}
      >
        Previous
      </Button>
      <Button
        onClick={handleNextPage}
        disabled={(currentPage + 1) * rowsPerPage >= launches.length}
      >
        Next
      </Button>
    </div>
  </div>
  )
}

export default App
