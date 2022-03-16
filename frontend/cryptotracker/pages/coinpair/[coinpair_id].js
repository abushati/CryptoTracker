function CoinPair (coinpair_id) {
    const [coinpairData, setData] = useState([])
    const [isLoading, setLoading] = useState(false)
    useEffect(() => {
        fetch('http://localhost:5000/coinpair/'+prop)
            .then((res) => res.json())
            .then((data) => {
                let coinpairs = data.coinpairs
                setData(coinpairs)
                setLoading(false)
            })
    }, [])
    return (
        <div>
            Hi from coin pair page
        </div>
    )
};
export default CoinPair
