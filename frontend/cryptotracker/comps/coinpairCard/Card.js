import Image from'next/image'
import styles from './card.module.css'
import Link from 'next/link'
import Modal from '../modal';
const {useEffect} = require("react");
const {useState} = require("react");

function Card (props){
  const [showModal, setShowModal] = useState(false);
    return (
      
        <div className={styles.card}>
          <Link href={"/coinpair/" + props.coinpair_id}>
            <div>
            <Image
              src="/images/cardano.png" // Route of the image file
              height={144} // Desired size with correct aspect ratio
              width={144} // Desired size with correct aspect ratio
              alt="Your Name"
            />
            <div>SYM: {props.coinpair_sym}</div>
            <div>Last Update: {props.price_update}</div>
            <div>Price: {props.price_value}</div>
            </div>
            </Link>
            <div><button onClick={() => setShowModal(true)}>Open Modal</button>
              <Modal
              onClose={() => setShowModal(false)}
                show={showModal}
                    >
               Hello from the modal!
            </Modal>
            </div>
        </div>
      
  )
}
export default Card