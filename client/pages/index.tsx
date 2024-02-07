import React, { useEffect, useState } from 'react';

function Index() {
  const [packages, setPackages] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5001/api/packages') // backend URL
      .then(response => response.json())
      .then(data => {
        setPackages(data);
      })
      .catch(error => {
        console.error('Error fetching packages:', error);
      });
  }, []);

  return (
    <div>
      <h1>Umrah Packages</h1>
      <ul>
        {packages.map((pkg, index) => (
          <li key={index}>
            <strong>{pkg['Umrah Travel Agent']}</strong>: {pkg['Package Details']} - {pkg['Price']}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Index;
