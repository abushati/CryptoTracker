import {useEffect, useState} from "react";

function Card (){
  const [data, setData] = useState(null)
  const [isLoading, setLoading] = useState(false)

  useEffect(() => {
  fetch('http://localhost:5000/coinpair/61f5814d32e2534f6e8e0ef7')
      .then((res) => res.json())
      .then((data) => {
        setData(data)
        setLoading(false)
      })
  }, [])


    return (
      <ul>
          t

      </ul>
  )
}
export default Card
