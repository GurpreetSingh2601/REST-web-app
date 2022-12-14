import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://lab6a.eastus2.cloudapp.azure.com/processing/stats`)
            .then(response => response.json())
            //.then(response => console.log(JSON.stringify(response)))
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                console.log(error)
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Parts Received</th>
							<th>Damaged Parts</th>
						</tr>
						<tr>
							<td># Num of orders: {stats['num_orders']}</td>
							<td># Num of damaged parts: {stats['num_damaged_part']}</td>
						</tr>
						<tr>
							<td colSpan="2">Max part number: {stats['max_part_number']}</td>
						</tr>
						<tr>
							<td colSpan="2">Max part price: {stats['max_part_price']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
