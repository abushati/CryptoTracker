import Image from'next/image'
import styles from './card.module.css'
import Link from 'next/link'

function Card (props){
    return (
      <Link href={"/coinpair/" + props.coinpair_id}>
        <div className={styles.card}>
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
  )
}
export default Card