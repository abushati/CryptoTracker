import { API } from "../config";


import Card from "../comps/coinpairCard/Card.js";
import AlertCard from "../comps/alertCards/alertCards"
import styles from "../styles/homeage.module.css"
import { AlertCardType } from "../comps/alertCards/alertCards";
import Button from '@mui/material/Button';

const {useEffect} = require("react");
const {useState} = require("react");

function Homepage () {
    const [data, setData] = useState([])
    const [userWatchlist, setUserWatchlist] = useState([])
    const [coinpairPage,setCoinpairPage] = useState(0)
    const [alerts,setAlerts] = useState([])
    
    const [coinpairCards, setCoinpairCards] = useState([])
    const [fetchingNewCoins, setFetchingNewCoins] = useState(false)
    const [alertCoinPairs, setAlertCoinPairs] = useState({})

    const [watchlistContent, setWatchlistContent] = useState([])
    const [generatedAlertsContent, setGeneratedAlertsContent] = useState([])
    const [alertContent, setAlertContent] = useState([])
    
    const [isLoading, setLoading] = useState(false)

    if (isLoading) return <p>Loading...</p>
    if (!data) return <p>No profile data</p>

    //Onmount init api calls to get the coins, user watchlist, user's alerts, etc
    useEffect(() => {
        fetch(`http://${API}/coinpairs`)
            .then((res) => res.json())
            .then((data) => {
                setData(data.coinpairs)   
        });
        fetch(`http://${API}/watchlist`)
        .then((res) => res.json())
        .then((data) => {
            setUserWatchlist(data.coinpairs)
        });
        fetch(`http://${API}/alerts`)
        .then((res) => res.json())
        .then((data) => {
            setAlerts(data.alerts)
        });
        setLoading(false)
    }, []);

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

    //Set the user watchlist cards, listening for changes to the userWatchlist so we can rerender the cards in watchlist section
    useEffect(() =>{
        let d = []
        if (userWatchlist.length != 0){
            d = userWatchlist.map((coin) => {
                return <Card coinInfo={coin}
                        props= {{watchlisted:true, updateWatchlist:updateWatchlist}}/>
                    }
                )    
            
            }
        createContent(d, 'watchlist')
        homepageCards()
    },[userWatchlist])

    //Used to set the homeage cards, so when the data from the api call is complete we create the cards
    useEffect(() =>{
        homepageCards()
    },[data])

    //homepage cards get generated when we know the watchlist cards. To avoid duplicate cards in watchlist and homepage. 
    const homepageCards = () => {
        const watchlistCoinIDs = userWatchlist.map(coin => coin.coinpair_id)
        const cards = 
            <div id={styles.hompageCards} >
                {data.map((coin) =>{
                    if (!watchlistCoinIDs.includes(coin.coinpair_id)){
                        return <Card coinInfo={coin}
                                    props={{watchlisted:false, 
                                            updateWatchlist:updateWatchlist}
                                        }/>}
                        }
                    )
                }
            </div>
        setCoinpairCards(cards)
    }

    const fetchCoinPair = async (coinpairId) => {
        const res = await fetch(`http://${API}/coinpair/${coinpairId}`)
        const json = await res.json()
        return json
    }

    //The paganation of the homepage cards so not all the coinpairs are loaded at once
    const fetchAdditionalCoins = () => {
        setFetchingNewCoins(true)
        let nextPage = coinpairPage + 1
        setCoinpairPage(nextPage)
        fetch(`http://${API}/coinpairs?offset=${nextPage}`)
        .then((res) => res.json())
        .then((json) => {
            setData(data => data.concat([ ...json.coinpairs]) )  
            setFetchingNewCoins(false)
    });
    
    }

    const createAlertCards = (alerts) => {
        console.log('Creating Information Alerts Cards')
        let t = alerts.map(e => {
                let coinpairInfo = e.coinpair
                let header = `Alert Type: ${e.alert_type}`
                let body = [`Coin Pair SYM: ${coinpairInfo.coinpair_sym}`,`Threshold: ${e.threshold}`, `Threshold condition: ${e.threshold_condition}`]

                return <AlertCard 
                            key={`${AlertCardType.INFO}:${e.alert_id}`}
                            cardHeader={header}
                            cardBody={body}
                            type={AlertCardType.INFO}
                            id={e.alert_id}
                            alertData={e}
                            coinInfo={coinpairInfo}  
                            />      
        })

        createContent(t, 'info')
        console.log('Finished Creating Information Alerts Cards')
    }

    const createGeneratedAlertCards = (alerts) => {
        let genCards = alerts.map(e => {
            let header = `${e.alert_type} alert triggered`.toUpperCase()
            
            // Only show the first alert generation, the rest will increment the counter on the card
            let occurances = e.generation_history.length
            let body = [`${e.generation_history[0].msg}`]
            return <AlertCard 
                    key={`${AlertCardType.GENERATION}:${e.generation_history[0]._id}`}
                    cardHeader={header}
                    cardBody={body} 
                    type={AlertCardType.GENERATION} 
                    id={e.generation_history[0]._id}
                    occurances={occurances}/>
        })
        
        console.log('Finished Creating Generated Alert Cards')
        createContent(genCards, 'gen')
    }

    //Get alerts that have been generated
    useEffect(() => {
        const genAlerts = alerts.filter(genAlert => {
            const genHistory = genAlert.generation_history
            if (genHistory.length > 0) 
                return genAlert
        })
        createAlertCards(alerts)    
        createGeneratedAlertCards(genAlerts)
    },[alerts])

    const createContent = (cards, type) => {
        let typeMapping = {
            'gen': {'setter':setGeneratedAlertsContent,'nullContent':<div className={styles.noContent}>No generated alerts</div>},
            'info':{'setter':setAlertContent,'nullContent':<div className={styles.noContent}>No alerts generated</div>},
            'watchlist':{'setter':setWatchlistContent,'nullContent':<div className={styles.noContent}>No watchlisted coins</div>}
        }
        console.log(cards)
        console.log(type)
        let setState = typeMapping[type]['setter']
        if (!cards.length) {
            setState([typeMapping[type]['nullContent']])
        } else {
            setState(cards)
        }
    }


    return (
        <div >
            <div style={{display:'flex',flexDirection:'row'}}>
                <div style={{width:'80%',margin: "0px 10px 0px 10px"}}>
                    <div style={{ borderBottom: '#0c1e31',borderBottomStyle: 'solid',padding: '0px 0px 30px 0px'}}>
                        <h1 className={styles.sectionTitle}>Watchlist</h1>
                            <div className={styles.watchlist}>
                                {watchlistContent}
                            </div>
                    </div>
                    <div>
                        <h1 className={styles.sectionTitle}>Coin Pairs</h1>
                            {coinpairCards}
                    </div>
                </div>
                <div style={{width:'20%',padding: '0px 10px', borderLeftStyle: 'outset',height: '100vh'}}>
                    <div style={{minHeight:'90px'}}> 
                        <h2 className={styles.sectionTitle}>Triggered alerts</h2>
                                {generatedAlertsContent}
                            
                    </div>
                    <div style={{minHeight:'90px'}}>
                        <h2 className={styles.sectionTitle}>My Alerts</h2>
                                {alertContent}
                    </div>
                </div>
            </div>
            <div id={styles.loadCoinsButtonCont}>
                <Button variant="outlined" onClick={() => fetchAdditionalCoins()}>{fetchingNewCoins? 'Loading..' : 'Load More'}</Button>
            </div>
            <div id="modal-root"></div>
        </div>
    )
};
export default Homepage