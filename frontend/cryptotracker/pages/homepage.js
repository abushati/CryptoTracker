import Card from "../comps/coinpairCard/Card.js";
import AlertCard from "../comps/alertCards/alertCards"
import styles from "../styles/homeage.module.css"
const {useEffect} = require("react");
const {useState} = require("react");

function Homepage () {

    const [data, setData] = useState([])
    const [userWatchlist, setUserWatchlist] = useState([])
    const [coinpairPage,setCoinpairPage] = useState(0)
    const [alerts,setAlerts] = useState([])
    const [generatedAlerts, setGeneratedAlerts] = useState([])
    
    const [watchlistCards, setWatchlistCards] = useState([])
    const [coinpairCards, setCoinpairCards] = useState([])
    const [generatedAlertsCards, setGeneratedAlertsCards] = useState([])
    const [alertCards, setAlertCards] = useState([])

    const [isLoading, setLoading] = useState(false)

    if (isLoading) return <p>Loading...</p>
    if (!data) return <p>No profile data</p>

    //Called from the card component when a card is added/removed to update userWatchlist then watchlist cards rerenders 
    const updateWatchlist = (action,coinpairId) => {
        if (action=='remove') {
            let updated = userWatchlist.filter((e) => e.coinpair_id != coinpairId)        
            setUserWatchlist(updated)
          }
        else if (action=='add'){
            for (const coinpair of data) {
                if (coinpair.coinpair_id == coinpairId){
                    setUserWatchlist([...userWatchlist, coinpair])
                    break
                }
            }  
        }
    }

    //homepage cards get generated when we know the watchlist cards. To avoid duplicate cards in watchlist and homepage. 
    const homepageCards = () => {
        const watchlistCoinIDs = userWatchlist.map(coin => coin.coinpair_id)
        const cards = 
            <div id={styles.hompageCards} >
                {data.map((coin) =>{
                    if (!watchlistCoinIDs.includes(coin.coinpair_id)){
                        return <Card coinpair_id={coin.coinpair_id}
                        coinpair_sym={coin.coinpair_sym}
                        price_update={coin.coinpair_price.insert_time}
                        price_value={coin.coinpair_price.price}
                        watchlisted={false}
                        updateWatchlist={updateWatchlist}/>}
                        }
                    )
                }
            </div>
        setCoinpairCards(cards)
    }

    const createAlertCards = (alerts) => {
        let html = alerts.map(e => {
            let header = `Alert Type: ${e.alert_type}`
            //Todo: Fix this as alert can have multiple generations
            let body = `Threshold: ${e.threshold} Threshold condition: ${e.threshold_condition}`
            return <AlertCard cardHeader={header} cardBody={body}/>
        })
        return html
    }

    //The paganation of the homepage cards so not all the coinpairs are loaded at once
    const fetchAdditionalCoins = () => {
        let nextPage = coinpairPage + 1
        setCoinpairPage(nextPage)
        fetch(`http://localhost:5001/coinpairs?offset=${nextPage}`)
        .then((res) => res.json())
        .then((json) => {
            setData(data => data.concat([ ...json.coinpairs]) )  
    });
    }

    //Onmount init api calls to get the coins, user watchlist, user's alerts, etc
    useEffect(() => {
        fetch('http://localhost:5001/coinpairs')
            .then((res) => res.json())
            .then((data) => {
                setData(data.coinpairs)   
        });
        fetch('http://localhost:5001/watchlist')
        .then((res) => res.json())
        .then((data) => {
            setUserWatchlist(data.coinpairs)
        });
        fetch('http://localhost:5001/alerts')
        .then((res) => res.json())
        .then((data) => {
            setAlerts(data.alerts)
        });
        setLoading(false)
    }, []);

    //Used to set the homeage cards, so when the data from the api call is complete we create the cards
    useEffect(() =>{
        homepageCards()
    },[data])

    //Set the user watchlist cards, listening for changes to the userWatchlist so we can rerender the cards in watchlist section
    useEffect(() =>{
        if (userWatchlist.length != 0){
            let d = <div className={styles.watchlist}>
                        {userWatchlist.map((coin) =>{return <Card coinpair_id={coin.coinpair_id}
                            coinpair_sym={coin.coinpair_sym}
                            price_update={coin.coinpair_price.insert_time}
                            price_value={coin.coinpair_price.price}
                            watchlisted={true}
                            updateWatchlist={updateWatchlist}/>})}
                </div>
        setWatchlistCards(d)
        }
        homepageCards()
    },[userWatchlist])

    //Get alerts that have been generated
    useEffect(() => {
        const genAlerts = alerts.filter(alert => {
            const genHistory = alert.generation_history
            if (genHistory.length > 0) 
                return alert
        })
        setGeneratedAlerts(genAlerts)

        let alertCards = createAlertCards(alerts)
        setAlertCards(alertCards)
    },[alerts])

    useEffect(() => {
        let html = generatedAlerts.map(e => {
            let header = `${e.alert_type} triggered`
            //Todo: Fix this as alert can have multiple generations
            let body = `${e.generation_history[0].msg}`
            return <AlertCard cardHeader={header} cardBody={body} border={true}/>
        })
        setGeneratedAlertsCards(html)
    //    console.log(generatedAlertsCards)
    },[generatedAlerts])

    return (
        <div>
            <div style={{display:'flex',flexDirection:'row'}}>
                <div style={{width:'90%'}}>
                    <div> Watchlist
                            {watchlistCards}
                    </div>
                    ___________________________________________________
                    <div> Coin Pairs
                        {coinpairCards}
                    </div>
                </div>
                <div style={{width:'10%'}}>
                <div> Triggered alerts
                        {generatedAlertsCards.map(e=>e)}
                    </div>
                    <div> My Alerts
                        {alertCards.map(e=>e)}
                    </div>
                </div>
            </div>
            <div onClick={fetchAdditionalCoins}>
                load more
            </div>

            <div id="modal-root"></div>
        </div>
    )
};
export default Homepage