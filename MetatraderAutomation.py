from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import os
import configparser
import subprocess
import shutil
import glob
import re
import struct
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

ERROR_PATTERN = re.compile(r"^(?:(?P<path>.+?)\s*)?" r"\(" r"(?P<row>\d+)," r"(?P<col>\d+)\)" r"\s*:\s*" r"(?P<type>error|warning)\s+" r"(?P<code>\d+)\s*:\s*" r"(?P<msg>.+)$")
OPT_CACHE_HEADER_SIZE_OFFSET = 0x1AC
OPT_CACHE_RESULT_SIZE = 344
OPT_CACHE_INPUT_TEXT = re.compile(rb"(?:[\x20-\x7e]\x00){3,}")

SET_MARKET_WATCH_EXPERT = bytes.fromhex(
    "455835017100ca174004000000000100e40400000000000000000000000000003cda5eb8c2d3bb99ae30783cb68da7c1000000000000000000000000"
    "000000000100000000000000000000000000000000000000000000000004000000000000610f0000610f000040010400000000000000000000000000"
    "00000000000000007ca53881456ee216bdd59df34bb3aa2770c77f79ce2d9c27e54b23adf83357e88022866a00000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000579700a5b88907289f805b3c44d054a1e3c18f128606b8abe3a08e4dbe2f32086dd0a76c"
    "2c49d7df7a1c5711b4caab05f1226ad68fa9337413fc8a40f27c197c531302996591624e0c7d901bd70a91b5dbdbb20e88344d3c1ff3cf653d72c461"
    "b685ca2cc13d9df22c79067bec0c3c53a634b8a2605ffc9c96a4ff979d5a020e758d83d2945ff4bc3fedb9730abada771de97bdb14469651bcd29cea"
    "7a7374b7011512e88f3018c93d5fb716e2ccdba4b30f5310006f1f06b09975d0586befd55affae497626ef3f1ad040721d6a7c2b75df8b7e15b2223e"
    "1154954c1c5affac54adb485a50ab221f3cb0f37b5f1b80f7f0d479949d0f72fad5fa81a4c742006b041e7edbde3d6b950855e10df8e17fe7e85dfff"
    "a1ac72636bd1ce5aff7ed71bd8a332feebb884a9e12265b0f42454a6d70c4f80b0e558ae1b29689740521406e34821182014adbeef9aef8c529dd1f5"
    "b31a6dd48fc82c04a1c3aa3d94d0f4579310b8e68a8fac31083d7204d1f36ca028a6b2c8291a887fbc869aba1410aee9e351951f1cadfea5616a5f67"
    "9aa3ef6839b51286b7bd356070e8ce6851978953904084f467fefcdeb6e482d1bd35a11166c5f0e6eb16e91b25567c8f0abd96db4ad1b9e4bdd97bd4"
    "b057d3dea47270afcf27cfcea0cbffafb3ca6146dec49747649e7e7e149469c55911ebce7d3513ee3c99de11eb8c10528b7a35e89334df999749f7ba"
    "e54b3a7afe6973ca6938b8f471add93d509f5d27cdcfb8400627a713be795d6c8cbed084803baace2ecc0b6c96ce4b2905f05878f749fcab73ca1eda"
    "a34aac1db0d9c2543ad9ea0f53c9cc3268becc2bb183219aa5b4c2ce5d9f4c6a2748b4187ae5dd8a9d136fbf89c31d2264afbf2c999d458ca05faffd"
    "ceae0fbdaa792bf20571fb44bb33b6662b4099a1327596d1af0f8b6dd0f29ee363369ef03754fa94e7eab6db135497e22656bbd6737388623fcea5d8"
    "ee20f0618463702d3e5d472d7fe5e4fdccf3f33c3b51b72c95ab21a210e8723515a03283e4e665125582996b06a8a54c2bece5bec5b68555b07601ac"
    "3438cbdaaa43bace5d373a7005165a5a416554a561875a88bbc410895ad633a7a260e6d996c64a046b60e4560cdf1dfba7c2d0f89114e72fdb85c1fe"
    "824ca06982e694a05c8239b19e0746205634da22cbf0ebd9c0a73d5dbb329ff47e9732e5b3db246ad81a177fd8ae6be4b156991a40f0d694dca751c2"
    "a7d2631eb89e4f120990c00eca4eb0ff0cb686573a4905cbb663bda8b45ae252a30ee2e9e80c5093528004e15ad6b98bc241578b7fd38e236e17f52e"
    "933d7e1cc6308b6228e53d5be686eae607e94b3a9c1062680de7fa8b9ac12b19289272700454eb8b572520450601b800ea888185188a6aebc63eced5"
    "19ba62b7a57464d4f144a8cd60c4d441aeb25aa18c6d86fa0eb055aba37ce3238ace79aa09403e6a03e6ffda036e4fd26464c88c7069e3378e87c660"
    "ae601c25531209c2b556cff369935300b6202e492cd9534140a7eaa8838205baab0ffd6b8da71892024efa40dc2908f3755909ac952b02911e16491a"
    "9140edc814c0ba486fabb7ee1ed0221069bc34474c9c47b3371c1ea0702f62c1837eff454ddfb63367ae63a4959e8fad9d8331ba8a0663d7080e86b1"
    "c1391fb9a4cd35870dc6be401f6edc9a1ab7336679e5f3de7d7bb6c7ea9f2268eab2409b0fdc5902751c914d4138db73e9849400469ce4a8ce5a9a5d"
    "a5879db95a151dac99d2fa7ea510ced15e22903b1f1187b4422d93d3a5f812453e0c765c757c554a807af0dbff6614a0288c7579bf86f6b0da088ff0"
    "6f51d8da55ffb455191447b1dc95b5f8bb0d2c4874f152c2c066da42c318231206d062f4617dc206c8c8b8f5581c83dab109f01bf410c17d18eb1c40"
    "43fa98b520292745f78d6b244a59ef0fcd8d525b6e3e9f2553fad7c26134d1af79b30d12549faf1c898d357c674861d5460b534aee248b65d5de7e87"
    "2345626de2826757935a9d4467162296d2ea69f2819a3e07be8305a4d6742eadd8b1ee938d1dfcc8f8397b2210e36c5db325a7cdd6920e99d715fce1"
    "1cd6936d41da684a57ebb22661a41dc04fe9c768ce5302a01ffd42a5c9bc8aad4d1bd82904217f955b9339367ed1b6579d7a73ff2b3ead7e74f1ec72"
    "5958a392a96513d6836208fddb4f2345110f41ab4c01608cde9cd669534558492278229607e4a8f39225aa7f0bdd2ed62575d11c547f75c1fa005260"
    "f8104e497aefcb7f50111ec0e9a5d53af8bf1fdd85d9f2c822d3cc8d2328db321d8ce20428cadc306089db78522253dd728485f1b1f709d278c5813e"
    "c7e1119e8d8772a290c269b06a2c06887358c78ad7b8cbb7c9efcfbdcce9df59adc84e20f2855ea0a8b8dd16e44c7d6755c326b02dbd7806b50b47a7"
    "5f4454cc2a38d071be229b474081ff59ebf4a38bc7b533671d45ef49c6d55c392c68eea4a582695cb2e50c0c660b5fd5f65fda0d9dcb1d8234ebf9fb"
    "ac83ae0e67995b1706606da68bac22fd6f675fc80832c407396f64affa58e1efdd152f66fd7c4e53aadbb99183402f3591441c6214224422c3cec7d6"
    "d8ea013a8707e186020471115340fb960bf04abaec70e0b5089d6c3a7916d744c2f96dfeacb6e098586b44e3170e9b3c4d2d07c6ed8477842e6e8a44"
    "e96bac3cb51e2a20e7898c729b08da77eb3c048f51617f215160f2a22317f450abc16031e8cfc9693df670e39f1d9204043927495f1be980ec180020"
    "4d973f8349ec387f6710e5e48d7fb23cc80da5fb0737e339d24d26f81e3988fe22705b1421270a4d74b37f3ce4821bb21e6a214645820740677a43dd"
    "ac127cdcf6cb3feec9ae13b8f3bc5778c05c6602ea231e6e79157d95cf57d080d98353c60d59c39c1f376f165d6a60f25e32594c9320f64d296f8df6"
    "d9b24da63c69139920c8a31d837bfee2dc09ba44a241b96da50ca87bde9a6322791c5393da82692d39e86d15431cca93b3ded772436819caa138f551"
    "140c1d107330043847666c3c86eb4a75102a431e5f884bb9eac8b618a817bddc042cefbbc44471b3b977d32033e7c99670e14cec07628f22820de65e"
    "d1c41d9c9427e09bc76e51de2a2eecb22c1927205418c2a4a55131ef6e2e2fea1de18c25a606709b62ec83f56dc76dbb99ca6644a9d12dbf085d8971"
    "a57740e0f04ce03e0ea8b230bc06fe311e856bad7672171985f3f43eaae75b2dc5ed8982afcc23cb271cb285540bc0f5f96224528072157a5dfb4471"
    "528b391c68c44b3badce8c6ed8aebaa23f6a4e68af5faf57045dadffc8218d5ccb175597938b1107902c0795ee7440cee6caecb96dfd2a253ec15030"
    "7a2b6240a257d12f1def27d077a71680fcc151faabeb0f8f71299b5f6b516ed8146c9d4f7627a53fed72c669c225d3150ec8272a298bf14a187f2c6f"
    "782172d8e195315b917ba56baf89e95df05c9c13452762f65353618c88f2cd5ea0dbc7d636881afff2a86b8cc30d085bcd483ce6d94745eed770900d"
    "040dcea61cb1464a1e136eb036dfe2f53d131b52d929a1bdd8866cde6f828ce97cc87603934ed92800ac77423fd6411e01d066da5b52706d6ca38ee6"
    "35bf83c08d2d17e61fbbe1e58297e13add0f0d179425ba38d731ea6142faaa3bbf055debf992de548ca9bf130064043f2fe70e80048ef87ef2c5209b"
    "fdb783309696ca3f8c81d7fcc0d32da57cfb77fdb89536123c047f7d96c529f82acd537e0a18644898a9873775fc1bdfa2c9ac499ebd8d8265dcb116"
    "d8ae4fbe0ed3a0b218cb19102c5d7ba0cf96b4dc7258b8b046d51f496f2bedc9d5e66c0be6aab130edd7ab171be87df08fac4c39a9073816c22d380b"
    "11997aec4eef8da9d3a6d3a353f5b3c1369cfb546269319b0316754d1ee67235f557d3ef015f6c3488117a12c57d99a6f314fa93b8ae5482e67baf9e"
    "3999bb9a2d574dbc6038e963b980e0aa5f1e17c541cacdaa104a017bd84d4991a8fb7609dc87cf7eabb963b505befec890e14f9a6cac3069d4bbcd8f"
    "851ababc0a8315dde41fe18f296ab3fdcbfe9ee4fe13d23ca82db78037231672721e36f5556aac242340471d05b4e65f805be88015349d222e05331e"
    "a8c7bb46e23fad708ed1d78c3bc5f6adab5a5902df4c06115c976199fb3bc9f8f881d5da4e01b74196dde038e9e83fd836641e7e908cfe4156f01c77"
    "483c6ed55b46f03381b8e6ee67446c22e495a231473fd0db7c15b8b1e43cda956426dbf811f1a3edafbf381c091cefd1909f2c8f784494b93dbcb9c4"
    "927dc5abff661555891db3ef74f46b998fd4344bd3598b5a5154c263d283a9e4d084f1b6305b31a5ea1f55fd3b72baee5dda1ff176cf5aedbdcf9dc0"
    "5ec7d9907362bab3b6da94484d6a56bb498169a588229d82609863137091cdeac5e90eb51957a11e9b5ec59e71c113ee8dbc377cad1ceec40c31688a"
    "36649e560497e2ca5bf8a35c064462c0f0c2ee0e5ad2580c0afb6e9e389bf35f006ba82ad8387bcf8bde58de160ed644576e790b249231ce8db0e8a4"
    "7f9a5b273d9ea6effe595f0f9b5bf53c4acb8395a96a954ab382265f9d112d5a06b8fdf6117af8696ebe4ffeba793aa47a28452d6073c68513daeac4"
    "dfd83bc5bc2078eb4773f0469722dac261a60252514a7b9aaaa4f5316eb7c18edad10d3deff7d5cb9a617a57c6b676674a0ba2076d0f6023a12ed21f"
    "22673a3975ba967758f8869dd6b152e9fb7bffad4ecfba9ca1dee94778d94c6f944a64bf54c0974dfe3f8e5c6f43eba326da86a12d47013edc12a327"
    "2c6834ee3faa54980d8f44ccd37aa8d1a94073a69d59a153d2c047a24d4a7f3995259cb511dd9798f5ad5c2824fbed84fae43e96858da751f724583e"
    "fce7a55eadc18c720f48f49f1ac0bbc21e0013a5287d8a419fdec6e92278557ec10e1b0e2b9a412a03b27a7ea60fc6bad82394f7d4cbb8687aee17cc"
    "66c3ab655dec7379f4fab7400dd6b3d69c7f2a9a6af57a68ef6994512c699bb9ec2b2864efa4f05981b63ea29091c2d82cea31581c75db2ef69b491b"
    "497d8e2e513dbe1f075958658d62f160b2dacf1081767e666d4170990d6d068853f6c09d713dd8e92dc201fc7fa3f72ddae3a7ce598329ee5e277f5d"
    "6119845df5c1eefad9b775719896fce84dc1ac73a29b2591d159e1fd40b4a18e526fccb6d6ab5f41ec231eb8a658ee482406c0f7d3b82365bf6f4e62"
    "e9457700c98dd74ed36dfa27104ad2fb571950e259277ec30045bdb1e943a5b5fbbcf6bfff57c071bafed56d56befdd2b3458f63c97b3098c85ff9d9"
    "74ab4e165a92c7edfd4143a04444aa0691f2c7725142a9ed03e8a7b16807d27df593e18dc787c8a9d6692b09021673e8b2db7b5c62ce2b41540f0d16"
    "5cad4a57454a4f2a4efd18642fc3fea496805701777998fc244c486f8583832ed86e3d0b356db8c4a93257e86d41604596be3178ea6bb9ef2c03ddfc"
    "bd366128677ab84271cdcaca069fd0030f4bf65131175b8a8d424967594fd2157a7e7b8661cb0dc65379a647e2b8af6cccdbbc68280f980cede13d2c"
    "786f54f8eb985bec295038301316ba198f125bf892df1a219a0873a8222e5cc1741c0aa4b9356e651a029ce85fb6cbf979f2784a7f07f55c54b7bd29"
    "d28e992c0852213aad735a35ca93b32469640ffb403a5d344281f712cebc5c2e34f6e0ec3c4e05dee6b60c5e919f9abb7a27c1a1cb4faa9bb6adab80"
    "f1b8472fd5e04d4112c42851af42558c157d6a616d725e5460cbc6c6ef9adbd80e8d200a249a8a294c2ca4d573ec3e61c5671746550597044370dac0"
    "a3ada4884e450bc2abaf01197ec69036e23ca2195a50a8e99cebaa8e7ea1ef6b52ea7b3f71a13a7f24b3cad27cd721cd832d07849c52ffce2af51631"
    "80a4411962b86a478ed192002f3187746c4b9912b12a7f463b8ea7d873085264d53eab64eac53bf842cf6aae63ebf9701154a46cafc162be10d28571"
    "f51a42d0b129f59272da93c8e8273897bf3b5b91221648232d19ed5b79d1d350ca3d46d1d118d9f2d3c17096af33b8db13a1bbc5cedd615424ad578f"
    "11a09223db9f191aa2efe3d7e921823c847853769b61f1d7f46b39f9e98d52843c319fd2af0a3a76e1c2716144547abe4eaebd6c5d87a561487241cb"
    "56b596c9571fd640c7776349c037836b7d53a166b212a72304b49f7b0960051318d8697d146d294dcc16242602e1f2b99351313525f7d8f7d96b3933"
    "acb048ab0f057ed1f334ec63b9ea3b5e2016a0a9648c769a0202f9f67167163194027601efc22918e7bf703cd0be7cea99d284225c2867d936b2b427"
    "ceddfb74adfe1e2d3222291e29928c868605039a493b0b71f4600521ecbcd7f3ec37f1b70a981fc9414001801391164d34c3f4321397fe50ef8892db"
    "a41a0c5711469e20b51135192490bc259dd5b8609981984d46b83d6e6b1f67ba881773e39caeea586182fd1becf4b8af74854999a99ea431c00ad84e"
    "e72ce06ab67e018abdae8f3f53faf232b7fdc89416cda068f683b83303ef18c5d20744e88f0789176f9a025476c454e4b1e1c7bac014f8ba72435353"
    "7c97fbf563d1ce0d5289dda8c300f157cc5c0a57f1ab1cf3af65515a2f55a3b670f8557bf4f7252af2c1520d78e46d1ef94b86684d9704c00e62203b"
    "3e1c4530c150247d88b37bcfac5cc1c2defe1f51213cffed1922ccf6f5abade1a9eac33e33e6b8456b9cecce6e386740ebf29c9df9e55660160d9616"
    "fa8faa5e94a06e4b1ef9ba9da6b7f8f478d97a29918ca20aec01fdfad6b4ca0d2d2070e43686a678287e311aef979223497665383b748e7f32ca6a76"
    "0dce6adff268c414de187277b9047d61a720a97ba9e12b58870eed293f8a49cb7373b5c705bfe52e4672f65b83c257ff1720d0cfde563cd6c1ea52a4"
    "eb08ae489b9e6a8faf8711d534c799ca9fa339e33ed07b9ee7b5f3a85cbae52f8dc1a82b9c97c7a54aaf54f2e266a5a12ae57cf26aa1a639100fa20b"
    "4ef21ef5c0a9a24febc8eb73398ec35896fcda6a2752c048ea18ef96c80b44844fa94540a7641c1216e398d28fc1f4f6afb09667cb8019e6059cd3b9"
    "6f6ce554827d744523837b01848501f3bee82476868915946e9a57b1f9ec93eea86ad2368187ee451c745b865f7b1d7652f97580461493ebcd1c3fae"
    "46b174e74e6a75555554cbb8082729e0401b8fe0bc43d0058c8c3842389451ee1c71160af482b966d326e9746e1094bfa6cab90ac6ecbfed202975ee"
    "bf3b980c376aa09ca54a12e77c35612624b85a89a5746824bb14107b75b869208eed336e32fdbc0ec119695e36b611ba3d020f6925ef0569d7fc2c17"
    "b0b844a272367a71b1e5e4e5c107ff0801e692d81dfe63c7f8423b8cd37629874ea641806e15718037472513b805471ddc2d5c2ff01516655b0e433f"
    "961031a9d20b05c1b639ae864b3a9599c7f9f8f366d43ba02703b23be0bfd8ff6587383b0cf6014a7a4f00f6bf078696aa40afb607b4a95e79222b32"
    "f4a71eef05e861b28886c5571f415a425139a16537c3b19b50a2d0565dfa6e3c9acbc772b11435aafeeda8f559288bcfd20fafe689900a046e8e526b"
    "445addc4469218b3e6eb2edb4502ed97e23f0a4de4430ae9102cc8a6edcfcbd8b2eadcb91f58f2170786b6dd0a47764ffacea32587b7b6a80650a71d"
    "22ac8d0171c4510c9ffd9e1db9062c9d4d6135f7fcadd852b0647a3f90fd579b64d16b749024bba91e3f3800ec63f495910531aac11df6dbadba343d"
    "e12c2461772272f8eab989c7837feb26053be56846d11c6535739bdfedd39228387b3a53499a588eb2b0dfdb4e5b5d9c109e99f3bb689e47970e7e05"
    "70d64f3528ce3357de4f5c0c2893350d5cf38e5c1709a793c00b46cf5fb41adc935e9a3bdbeab2af2a8edf59fa0d85b1e6ae7ecc54028c3ad440abea"
    "ddf6e32913cb2663bf30cf715f951b1010e5ef51381be94c225117345a130d3b029a70ba787e3b4fdf2a0b31ae954981af0cf292ea0d4160d9565291"
    "6c8d2f55602306e31621e417679bda03c14384937b0a1f61e8fe81c70e1e0b896fbff1c3e38440ac3d709de6155900f63adf753194a7184fe190372a"
    "1f577572f9b3e410bb03698765ac1651397cae1f2dec7253434052673cee7757c9342ecb1ca3792db673797ef89c8ec56f8f6c05a63e9ab6d8d79865"
    "ae169e2f423fada08867c0b9a816a5fa86dbc476ae30464279a527c1c9c20890c022b1051f087c21fd7a8a996ee3f88573399b8134d3989b3977ead6"
    "c9b4f73991f28d74392c32b7593fdc89b295db9794762c115f5aed6f7eddfb9ef83eab5c5dab90ff62b5e1026841107a29c30ed08413e691cfa0fc7d"
    "3acc0cf5b24b129bfd5ee7c318eb541be9c3ddd72ba747cabc8e6f227458af086968647e00048b230d994430fd6b5f748073e802ca8814c19970cab7"
    "0ed270d28dc3d0bcc2676102d47853b43da0562957d9a38ac601568b57374c6253ec773fa1d38f8790d59318f0b33fca5e34272072dcd5ec6a41fdc1"
    "c17a3766814e1ea1f119f16a8f11a118cc477ac7db0604a14abe6d1cc0baeb796f83bcc8b6364396d1b92c7c45ff7ceab2d1086d270abe12d58da41b"
    "8a0917b4e21758b80c99fb8c338f0859d39fee868d5132c227504e11cd37c2394fa3484b170d83b74b77ac7d900c76ab4d67bc5eade009cdca51a8c7"
    "9c47dc71f76b306ca9359c1b3e7dd4f91413087b11ad5093b925d09c0223c54bc099eb42af8f1c1120dd69819863b1b24547cc82df039381baea13e2"
    "92b616ef5f07e874fd149e05206d931ad4b6cb8d65b102f81658379feef67c9754f6a1aa2dcafeb5c47d2c5bf1254697c23208d1f4e72253f6dc20f3"
    "03e89ca9b73871c8fac7acc44918393e6d4ad32ca48ae83b08bec0b66f35170a4d5977dc470c3014dd23fc470f15ad10358c42efccf06ea8474bb64d"
    "d39560cb53d1758e9dfa76814715135272ca6bc373a0041a7d51eb7945007da3d6fbfa4edb775f63abb3d13aefe30b0e490469070cc1094934c4bd28"
    "4639be0d05de84e4cbefde2feb11e412454e9a138bd61a5ffcd32b4f7d9526763698b42c2966949749c06a2fa29d1bfa07e6a0282afcb7e84e60dd39"
    "af1c57033a7eb892e95c7ec8f225be198444a41f5d311395021f6efcd29ba990a825382e914660c2300a21fca8de8f8d926549d9ea6538948e4f2b44"
    "969c16ad9814c5b09a6c266279f85dd3f1a54dadd0919faa99c94ea035dace251273eb16269e841e09329aec3350f690e3e678faba9c103cc49f41a4"
    "98923b4cc3dea061f67badbf3010835dda89e673e7e515782235f782d104b3b68c7e880e2ffca285312b6be291b1427240e573ed46afc408bf73576d"
    "c1cb5c56a6ddb6fccacff55c7520a35db3be39186351c01f69f34d7ec05fe7322f474c2b9d5ec6ffc42438be45499f4b3712bde15ada1d6b76deba5b"
    "626d6202b6cf18f7eee6333f79be8a0a139e46bd633264742a11355beb9cfb70cf5214f825d70fa94884ffb0608df1076a3edc2ae6ca3ba11f8e2e3a"
    "523750e17fd1f7a0f591a749fca9f32bf6e11b6e04613b323e881e1c1e2c69a1827d5fd89e1ff321545da922f36fcc407177ef1a2aa2416b40a8930c"
    "22ab929cf73b89470edb88aa3867c70046aae0c5cdb32675fe70aa1e2ddc3999eb599a94416f11fdb359bb3b6c3993eeb4fb24118040761e45597c1f"
    "40be32e1327b4a7e1c099870580a7a37030ae76eec6e083639b3df4331b996bb85d4cfc848bafa704776bd8586e5f12ad1c13a036f69f9dc218365dc"
    "81b0353ceb89087d014c1722d345f0a2cc9e00fce487561f5085c8f9295ea3e7a9a999d639fd64bb25ee21df0ab5b6b8de80305956fa529541ab421a"
    "50305ad5bcead595c42ef8add0f28c7f45ac4f1232e525e4a8b43e0eb9a312aebf57bed15f18c6087cfad99c88ac94f296b7b36a0f57b07782d40e6b"
    "c0c5cc645d3766106df709b9a362b94788f2fdb679d821477ec92b64472cf765203f2c970b94940a4732f394b5cb3b4976e2801e28dbf255ae9dcebf"
    "6bccd2a84f016ac10e9bacf706bbb00a0786d91ccff1808173fec8e45175d3578b7309b9d33d4393af973da73d3a5ff0ab690e645c35db3b22463586"
    "42683b699ca5ff5b22bd1cb34b757161b36042e89af71d4c525b43fe182fb9fd3475b8034777a7f92a5fa2d303387dc1200c87746e5b44f76397009b"
    "e86d898ead718a3d7d8bc3cf1fec4e1417ce90ebbcaaf04c0af218608dce1f3315857239a7439b25c53c47987a85e28031e7ae8b83a6b19640e15a2e"
    "51cd675b54c7eedb073394580b647a722de5e64445db22452f6e150601eee990776828c501ba3f4333022d5fde233bdd31c2820990348b3a51c9fafb"
    "156471730b9106d765cfe90e7a9b499270ad9cdbeaee4a99ed9a8dad5d28155e61c2177ad0573b0ffba3055f4835b55dfa9de981d81d472a82925aeb"
    "2d8e8650512a82e3d37335a51965c3efafc9c959dd42a60b4fbc376fe0a014a308670c09d5fe5b67d698c834e1fa408c036a8b8d5d7048cf8a7e5f56"
    "905429d986d84e668db8cad58155bfe11becb6ee0d7a5accd84778e4ac81ec76bb04b2aa3f69231874a7b94fee3b5c6f6d78b8663d43bb2a9369f0cd"
    "156fdcf11c617642cd6932ce903dc07124f5db0ecc4dfe75be91d639eb1139cb4ae46e93414f966892b314504f27d6a35c59cc6c291d303fe9036736"
    "555077ac294e7051fda41abe2cbede7ae813ac86c147efbf147e20f50d08f9426ca9cb0a191d6ab90dbac48b3b06f33c3fa0b01436bd9165335e273e"
    "2714943cd97cc860b7fc2609617139ca0c6d652f4c088c43965c65371b3d350b7e3590e4871512590b908e5b472c7333e9d143bc8d0c31f752a307cd"
    "5e27f8a33134ae0082e23f46c483a0fc606c35634de6ac2b1688534ba2ac5dc17a67f46bfeb2920808ccbba7efed6bbd68928f02af7a479093f43667"
    "aebd916551f965bfa89515bd5afd49e1387da78ae2f2670911bd091393329233026ce567928a33e415810fa9df63bede7effdc0eedbd"
)


class Timeframe(Enum):
    M1 = "M1"
    M2 = "M2"
    M3 = "M3"
    M4 = "M4"
    M5 = "M5"
    M6 = "M6"
    M10 = "M10"
    M12 = "M12"
    M15 = "M15"
    M20 = "M20"
    M30 = "M30"
    H1 = "H1"
    H2 = "H2"
    H3 = "H3"
    H4 = "H4"
    H6 = "H6"
    H8 = "H8"
    H12 = "H12"
    D1 = "D1"
    W1 = "W1"
    MN1 = "MN1"


class BacktestModel(Enum):
    EVERY_TICK = 0
    ONE_MINUTE_OHLC = 1
    OPEN_PRICES_ONLY = 2
    MATH_CALCULATIONS = 3
    REAL_TICKS = 4


class BacktestMode(Enum):
    RANDOM_DELAY = -1
    NORMAL = 0


class BacktestOptimization(Enum):
    DISABLED = 0
    SLOW_COMPLETE = 1
    FAST_GENETIC = 2
    # Note: using this will produce an empty report and get stuck with only 2 symbols
    ALL_MARKET_WATCH_SYMBOLS = 3


class BacktestOptimizationCriterion(Enum):
    MAXIMUM_BALANCE = 0
    BALANCE_PROFITABILITY = 1
    BALANCE_EXPECTED_PAYOFF = 2
    BALANCE_DRAWDOWN = 3
    BALANCE_RECOVERY_FACTOR = 4
    BALANCE_SHARPE_RATIO = 5
    CUSTOM = 6
    COMPLEX_CRITERION = 7


class BacktestForwardMode(Enum):
    OFF = 0
    HALF = 1
    THIRD = 2
    QUARTER = 3
    CUSTOM = 4


@dataclass
class BacktestConfig:
    Symbol: str = "EURUSD"
    Period: Timeframe = Timeframe.M5
    Model: BacktestModel = BacktestModel.REAL_TICKS
    ExecutionMode: BacktestMode | int = 50
    Optimization: BacktestOptimization = BacktestOptimization.DISABLED
    OptimizationCriterion: BacktestOptimizationCriterion = BacktestOptimizationCriterion.BALANCE_PROFITABILITY
    FromDate: str = "2024.01.01"
    ToDate: str = "2025.01.01"
    ForwardMode: BacktestForwardMode = BacktestForwardMode.OFF
    ForwardDate: str = "2024.09.01"
    Deposit: float = 5000
    Leverage: str = "1:100"
    ReplaceReport: bool = True
    ReportName: str = "BacktestResult.htm"
    ShutdownTerminal: bool = True
    Visual: bool = False
    UseLocal: bool = True
    UseRemote: bool = False
    UseCloud: bool = False


def FindMetaQuotes() -> Path:
    # Locate terminal data directories in MetaTrader's per-user storage.
    appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    terminal_root = appdata / "MetaQuotes" / "Terminal"
    candidates = sorted(path for path in terminal_root.iterdir() if path.is_dir() and (path / "MQL5").is_dir()) if terminal_root.is_dir() else []

    # A data directory must be selected explicitly when multiple terminals exist.
    if not candidates:
        raise FileNotFoundError(f"No MetaTrader terminal data directory found in {terminal_root}")
    if len(candidates) > 1:
        raise RuntimeError(f"Multiple MetaTrader terminal data directories found in {terminal_root}: {', '.join(map(str, candidates))}")
    return candidates[0]


def FindMetaEditor(metaquotes: Path) -> Path:
    # Validate the terminal data directory before resolving its installation.
    metaquotes = Path(metaquotes)
    if not metaquotes.is_dir() or not (metaquotes / "MQL5").is_dir():
        raise ValueError(f"Invalid MetaTrader terminal data directory: {metaquotes}")

    # Read the terminal's recorded installation location, including UTF-16 origin files.
    origin = metaquotes / "origin.txt"
    if origin.is_file():
        origin_text = origin.read_bytes().decode("utf-16", errors="ignore")
        paths = re.findall(r"[A-Za-z]:[\\/][^\x00\r\n]+", origin_text)
        for recorded_path in paths:
            installation = Path(recorded_path.strip().strip('"'))
            if installation.suffix.lower() == ".exe":
                installation = installation.parent
            for name in ("MetaEditor64.exe", "MetaEditor.exe"):
                editor = installation / name
                if editor.is_file():
                    return editor

    # Fall back to a uniquely installed editor when origin metadata is unavailable.
    roots = {Path(path) for path in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")) if path}
    candidates = sorted({editor for root in roots if root.is_dir() for name in ("MetaEditor64.exe", "MetaEditor.exe") for editor in root.rglob(name)})
    if not candidates:
        raise FileNotFoundError(f"No MetaEditor executable found for terminal data directory {metaquotes}")
    if len(candidates) > 1:
        raise RuntimeError(f"Multiple MetaEditor executables found; unable to identify the one for {metaquotes}: {', '.join(map(str, candidates))}")
    return candidates[0]


def StartTerminal(metaeditor: Path, args: str = "", background: bool = True):
    # Validate the editor path and select the terminal architecture that matches it.
    metaeditor = Path(metaeditor)
    if not metaeditor.is_file():
        raise FileNotFoundError(f"MetaEditor executable not found: {metaeditor}")

    terminal_path = os.path.join(os.path.dirname(metaeditor), "Terminal64.exe")

    # Keep a caller-provided command line intact so Windows parses its quoted options.
    command = [str(terminal_path)] if not args.strip() else f'"{terminal_path}" {args}'

    # Start the terminal minimized when it should run in the background.
    startupinfo = None
    if os.name == "nt" and background:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 7

    return subprocess.Popen(command, startupinfo=startupinfo)


def SetMarketWatch(metaquotes: Path, metaeditor: Path, Symbols: list[str]):
    # Create set market watch expert
    DestinationDir = os.path.join(metaquotes, "MQL5/Scripts/MetatraderAutomation")
    Destination = os.path.join(DestinationDir, "SetMarketWatch.ex5")
    os.makedirs(DestinationDir, exist_ok=True)
    with open(Destination, "wb") as f:
        f.write(SET_MARKET_WATCH_EXPERT)

    # Store the requested EA input where the terminal can load startup presets.
    PresetPath = Path(metaquotes) / "MQL5" / "Presets" / "SetMarketWatch.set"
    PresetPath.parent.mkdir(parents=True, exist_ok=True)
    PresetPath.write_text(f"IN_SYMBOLS={','.join(Symbols)}\n", encoding="ascii")

    # Create the startup configuration and load the generated EA preset.
    ConfigPath = Path(os.path.abspath("SetMarketWatch.ini"))
    Config = configparser.ConfigParser()
    Config.add_section("Experts")
    Experts = Config["Experts"]
    Experts["Enabled"] = "1"
    Experts["AllowLiveTrading"] = "0"
    Experts["AllowDllImport"] = "0"
    Config.add_section("StartUp")
    StartUp = Config["StartUp"]
    StartUp["Script"] = "MetatraderAutomation/SetMarketWatch.ex5"
    StartUp["ScriptParameters"] = PresetPath.name
    StartUp["Symbol"] = "EURUSD"
    StartUp["Period"] = "H1"
    StartUp["ShutdownTerminal"] = "1"
    with open("SetMarketWatch.ini", "w") as f:
        Config.write(f)

    # start metatrader
    proc = StartTerminal(metaeditor, f'/config:"{ConfigPath}"')
    proc.wait()

    # remove temp files
    ConfigPath.unlink(missing_ok=True)
    PresetPath.unlink(missing_ok=True)


def RemoveBacktestCache(metaquotes: Path, strategy: str, symbol: str, timeframe: Timeframe):
    # Restrict deletion to cache files for the requested expert, symbol, and period.
    cache_directory = Path(metaquotes) / "tester" / "cache"
    strategy_name = Path(strategy).stem
    cache_prefix = f"{strategy_name}.{symbol}.{timeframe.value}."

    # A missing cache directory means no backtest artifacts have been created yet.
    if not cache_directory.is_dir():
        return

    # Cache filenames can have multiple extensions, so remove every matching file.
    for cache_file in cache_directory.glob(f"{glob.escape(cache_prefix)}*"):
        if cache_file.is_file():
            cache_file.unlink()


def GetProgramType(compiled_path: Path | str):
    # Validate the supplied file before reading its compiled header.
    try:
        compiled_path = Path(compiled_path)
        if not compiled_path.is_file():
            return "unknown"
        with compiled_path.open("rb") as file:
            header = file.read(4)
    except (OSError, TypeError, ValueError):
        return "unknown"

    # The low nibble of the fourth header byte identifies the program type.
    if len(header) < 4:
        return "unknown"
    program_type = header[3] & 0x0F
    if program_type == 1:
        return "script"
    if program_type == 2:
        return "expert"
    if program_type == 4:
        return "indicator"
    return "unknown"


def CreateBacktestFile(BacktestFilePath: str, ExpertPath: str, Backtest: BacktestConfig | None = None, Inputs=None):
    # Use the standard backtest settings when no custom configuration is provided.
    Backtest = Backtest or BacktestConfig()

    # Create the tester configuration from the typed backtest settings.
    Config = configparser.ConfigParser()
    Config.add_section("Tester")
    TesterSect = Config["Tester"]
    TesterSect["Expert"] = ExpertPath
    TesterSect["Symbol"] = Backtest.Symbol
    TesterSect["Period"] = Backtest.Period.value
    TesterSect["Model"] = str(Backtest.Model.value)
    TesterSect["ExecutionMode"] = str(Backtest.ExecutionMode.value if isinstance(Backtest.ExecutionMode, BacktestMode) else Backtest.ExecutionMode)
    TesterSect["Optimization"] = str(Backtest.Optimization.value)
    TesterSect["OptimizationCriterion"] = str(Backtest.OptimizationCriterion.value)
    TesterSect["FromDate"] = Backtest.FromDate
    TesterSect["ToDate"] = Backtest.ToDate
    TesterSect["ForwardMode"] = str(Backtest.ForwardMode.value)
    TesterSect["ForwardDate"] = Backtest.ForwardDate
    TesterSect["Deposit"] = str(Backtest.Deposit)
    TesterSect["Leverage"] = Backtest.Leverage
    TesterSect["ReplaceReport"] = str(int(Backtest.ReplaceReport))
    TesterSect["ShutdownTerminal"] = str(int(Backtest.ShutdownTerminal))
    TesterSect["Visual"] = str(int(Backtest.Visual))
    TesterSect["Report"] = Backtest.ReportName
    TesterSect["UseLocal"] = str(int(Backtest.UseLocal))
    TesterSect["UseRemote"] = str(int(Backtest.UseRemote))
    TesterSect["UseCloud"] = str(int(Backtest.UseCloud))

    # Add the expert input parameters.
    Config.add_section("TesterInputs")
    TesterInputsSect = Config["TesterInputs"]

    if Inputs is not None:
        for Key, Value in Inputs.items():
            TesterInputsSect[Key] = str(Value)

    # Write the MetaTrader configuration file.
    with open(BacktestFilePath, "w") as f:
        Config.write(f)


def CompileMQ5(metaquotes: Path, metaeditor: Path, SourcePath: Path):
    Include = os.path.join(metaquotes, "MQL5")

    # Create Log File
    FileWithoutExt, FileExt = os.path.splitext(SourcePath)
    LogFile = FileWithoutExt + ".log"
    open(LogFile, "w").close()

    try:
        # Start compilation with each command argument preserved as a separate value.
        Command = f'"{metaeditor}" /compile:"{SourcePath}" /include:"{Include}" /log:"{LogFile}"'
        EditorProc = subprocess.Popen(Command)
        EditorProc.wait()

        # Read Log
        Errors, Warnings = ParseCompileLog(LogFile)
        return Errors, Warnings
    finally:
        # Delete the temporary log even when compilation or parsing fails.
        if os.path.exists(LogFile):
            os.remove(LogFile)


def RunBacktestFile(metaquotes: Path, metaeditor: Path, BacktestFilePath: Path, ResultFileName: str):
    ReportPath = os.path.join(metaquotes, ResultFileName + "htm")
    OptimizationPath = os.path.join(metaquotes, ResultFileName + ".xml")
    SymbolsOptimizationPath = os.path.join(metaquotes, ResultFileName + ".symbols.xml")

    if os.path.exists(ReportPath):
        os.remove(ReportPath)
    if os.path.exists(OptimizationPath):
        os.remove(OptimizationPath)
    if os.path.exists(SymbolsOptimizationPath):
        os.remove(SymbolsOptimizationPath)

    proc = StartTerminal(metaeditor, "/config:" + str(BacktestFilePath))
    return proc.wait()


def RunBacktestConfig(metaquotes: Path, metaeditor: Path, ExpertPath: str, Backtest: BacktestConfig | None = None, Inputs=None):
    ConfigPath = Path(os.path.join(Backtest.ReportName + ".ini"))
    CreateBacktestFile(ConfigPath, ExpertPath, Backtest, Inputs)
    RunBacktestFile(metaquotes, metaeditor, ConfigPath, Backtest.ReportName)
    ConfigPath.unlink(missing_ok=True)


def ParseCompileLog(LogFilePath: str):
    Errors = []
    Warnings = []
    with open(LogFilePath, "r", encoding="utf-16", errors="replace") as File:
        for Line in File:
            if Line:
                StrippedLine = Line.strip()
                M = ERROR_PATTERN.match(StrippedLine)
                if M:
                    if M.group("type") == "warning":
                        Warnings.append({"Path": M.group("path"), "Row": M.group("row"), "Column": M.group("col"), "Code": M.group("code"), "Message": M.group("msg")})
                    else:
                        Errors.append({"Path": M.group("path"), "Row": M.group("row"), "Column": M.group("col"), "Code": M.group("code"), "Message": M.group("msg")})

    return Errors, Warnings


def ParseBacktest(metaquotes: Path, ResultFileName: str):
    Result = {"Backtest": {}, "HistoryDeals": []}
    ResultFilePath = os.path.join(metaquotes, ResultFileName + ".htm")
    try:
        with open(ResultFilePath, "r", encoding="utf-16") as file:
            ResultFile = file.read()
    except UnicodeDecodeError:
        with open(ResultFilePath, "r", encoding="latin-1") as file:
            ResultFile = file.read()
    except FileNotFoundError:
        Result["Error"] = f"File not Found"
        return Result
    try:
        HTML = BeautifulSoup(ResultFile, "html.parser")
    except Exception as e:
        Result["Error"] = f"{e}"
        return Result

    txt = lambda s: re.sub(r"\s+", " ", (s or "").strip())

    def after(label):
        td = HTML.find("td", string=lambda t: t and txt(t) == label)
        if not td:
            return None
        nxt = next((x for x in td.next_siblings if getattr(x, "name", None) == "td"), None)
        if not nxt:
            return None
        b = nxt.find("b")
        return txt(b.get_text() if b else nxt.get_text())

    def DealTypeToNumber(Type):
        if Type == "balance":
            return 2
        elif Type == "buy":
            return 0
        elif Type == "sell":
            return 1
        return -1

    Backtest = {
        "Expert": after("Expert:"),
        "Symbol": after("Symbol:"),
        "Period": after("Period:"),
        "Currency": after("Currency:"),
        "InitialDeposit": after("Initial Deposit:"),
        "Leverage": after("Leverage:"),
    }

    if not Backtest["Symbol"]:
        Result["Error"] = "Symbol missing"
        return Result

    # Find Backtest Results
    ResultsDiv = HTML.find("div", string=lambda t: t and txt(t).lower() == "results")
    if ResultsDiv:
        table = ResultsDiv.find_parent("table")
        start_tr = ResultsDiv.find_parent("tr")
        for tr in start_tr.find_all_next("tr"):
            if tr.find_parent("table") != table:
                break
            if tr.find("img"):
                continue
            tds = tr.find_all("td")
            if not tds:
                continue
            i = 0
            while i < len(tds) - 1:
                label = txt(tds[i].get_text())
                if label.endswith(":"):
                    j = i + 1
                    while j < len(tds) and not txt(tds[j].get_text()):
                        j += 1
                    if j < len(tds):
                        b = tds[j].find("b")
                        val = txt(b.get_text() if b else tds[j].get_text())
                        Backtest[label[:-1]] = val
                        i = j + 1
                    else:
                        i += 1
                else:
                    i += 1

    Result["Backtest"] = Backtest

    # Find Deals
    deals_title = HTML.find("div", string=lambda t: t and txt(t).lower() == "deals")
    if deals_title:
        table = deals_title.find_parent("table")
        title_tr = deals_title.find_parent("tr")

        # find the first header row *after* the Deals title (bgcolor="#E5F0FC")
        header_tr = None
        for sib in title_tr.find_next_siblings("tr"):
            if sib.find_parent("table") != table:
                break
            if sib.get("bgcolor") and re.search(r"#E5F0FC", sib.get("bgcolor"), re.I):
                header_tr = sib
                break
        if header_tr:
            headers = [txt(th.get_text()) for th in header_tr.find_all(["th", "td"])]
            for tr in header_tr.find_next_siblings("tr"):
                if tr.find_parent("table") != table:
                    break
                # stop if we somehow hit another titled section
                if tr.find("div") and tr.find("div").find("b"):
                    break
                tds = tr.find_all("td")
                # skip totals/spacers with colspans or wrong length
                if len(tds) != len(headers):
                    continue

                def AsFloat(Value):
                    if Value:
                        if isinstance(Value, str):
                            Value = Value.replace(" ", "")
                        return float(Value)
                    else:
                        return 0.0

                Deal = {headers[i]: txt(tds[i].get_text()) for i in range(len(headers))}
                Result["HistoryDeals"].append(
                    {
                        "ticket": 0,
                        "order": Deal["Order"],
                        "time": Deal["Time"],
                        "time_msc": 0,
                        "type": DealTypeToNumber(Deal["Type"]),
                        "entry": 0 if Deal["Direction"] == "in" else 1,
                        "magic": 0,
                        "position_id": int(Deal["Deal"]),
                        "reason": 0,
                        "volume": AsFloat(Deal["Volume"]),
                        "price": AsFloat(Deal["Price"]),
                        "commission": AsFloat(Deal["Commission"]),
                        "swap": AsFloat(Deal["Swap"]),
                        "profit": AsFloat(Deal["Profit"]),
                        "fee": 0.0,
                        "symbol": Deal["Symbol"],
                        "comment": Deal["Comment"],
                        "external_id": "",
                    }
                )

    return Result


def ParseOptimization(metaquotes: Path, ResultFilePath: str):
    Result = {"Optimization": []}
    ResultFilePath = os.path.join(metaquotes, ResultFilePath + ".xml")

    # Load the finalized SpreadsheetML report, allowing MetaTrader reports with a BOM.
    try:
        with open(ResultFilePath, "rb") as File:
            Workbook = ET.parse(File).getroot()
    except FileNotFoundError:
        Result["Error"] = "File not Found"
        return Result
    except (ET.ParseError, OSError) as Error:
        Result["Error"] = str(Error)
        return Result

    # Locate the first worksheet table without depending on SpreadsheetML prefixes.
    Table = next((Element for Element in Workbook.iter() if Element.tag.endswith("}Table")), None)
    if Table is None:
        Result["Error"] = "Optimization table missing"
        return Result

    Rows = [Element for Element in Table if Element.tag.endswith("}Row")]
    if not Rows:
        Result["Error"] = "Optimization headers missing"
        return Result

    def CellValues(Row):
        Values = []
        for Cell in Row:
            if not Cell.tag.endswith("}Cell"):
                continue
            Index = Cell.get("{urn:schemas-microsoft-com:office:spreadsheet}Index")
            if Index:
                Values.extend([None] * (int(Index) - len(Values) - 1))
            Data = next((Element for Element in Cell if Element.tag.endswith("}Data")), None)
            if Data is None:
                Values.append(None)
                continue
            Value = Data.text or ""
            DataType = Data.get("{urn:schemas-microsoft-com:office:spreadsheet}Type")
            if DataType == "Number":
                Number = float(Value)
                Value = int(Number) if Number.is_integer() else Number
            elif DataType == "Boolean":
                Value = Value == "1"
            Values.append(Value)
        return Values

    # Use the first row as column names and map each optimization pass to it.
    Headers = CellValues(Rows[0])
    if not any(Headers):
        Result["Error"] = "Optimization headers missing"
        return Result
    for Row in Rows[1:]:
        Values = CellValues(Row)
        if not any(Value is not None for Value in Values):
            continue
        Result["Optimization"].append({Header: Values[Index] if Index < len(Values) else None for Index, Header in enumerate(Headers) if Header})

    # A header-only report means every tester pass failed or no passes were scheduled.
    if not Result["Optimization"]:
        Result["Error"] = "Optimization completed without result rows; inspect the MetaTrader Tester log for failed passes"

    return Result


def _ReadOptimizationCacheText(Data: bytes, Offset: int):
    # Decode a null-terminated UTF-16LE field without matching an odd-byte null.
    End = next((Index for Index in range(Offset, len(Data) - 1, 2) if Data[Index : Index + 2] == b"\x00\x00"), len(Data))
    return Data[Offset:End].decode("utf-16-le", errors="replace")


def _GetOptimizationCacheInputDescriptors(Data: bytes, HeaderSize: int):
    # Collect input labels from the variable descriptor region after the fixed header.
    Names = []
    SeenNames = set()
    for Match in OPT_CACHE_INPUT_TEXT.finditer(Data[0x580:HeaderSize]):
        Name = Match.group().decode("utf-16-le")
        if len(Name) >= 4 and Name not in SeenNames:
            Names.append((Name, Match.start() + 0x580, Match.end() + 0x580))
            SeenNames.add(Name)

    # Pair each name with the following storage-offset and storage-width descriptor.
    Descriptors = []
    Widths = {1, 2, 4, 8, 16, 32, 64, 128, 256}
    for Index, (Name, _, End) in enumerate(Names):
        NextStart = Names[Index + 1][1] if Index + 1 < len(Names) else HeaderSize
        Candidates = []
        for Position in range(End, NextStart - 7):
            Offset, Width = struct.unpack_from("<II", Data, Position)
            if Offset < 0x10000 and Width in Widths:
                Candidates.append((Position, Offset, Width))
        if Candidates:
            Position, Offset, Width = Candidates[-1]
            Descriptors.append({"name": Name, "offset": Offset, "width": Width, "optimized": struct.unpack_from("<I", Data, Position - 12)[0] == 1})
    return Descriptors


def _ParseOptimizationCacheInputs(Data: bytes, HeaderSize: int, Descriptors=None):
    # Decode the static values stored in the input buffer described by each field.
    Descriptors = Descriptors if Descriptors is not None else _GetOptimizationCacheInputDescriptors(Data, HeaderSize)

    # Derive the buffer start from the descriptor with the largest storage extent.
    if not Descriptors:
        return {}
    BufferSize = max(Descriptor["offset"] + Descriptor["width"] for Descriptor in Descriptors)
    BufferStart = HeaderSize - BufferSize
    if BufferStart < 0 or BufferStart + BufferSize > len(Data):
        return {}

    # Decode integers, doubles, and fixed-width UTF-16 strings from the input buffer.
    Inputs = {}
    for Descriptor in Descriptors:
        Name = Descriptor["name"]
        Offset = Descriptor["offset"]
        Width = Descriptor["width"]
        ValueOffset = BufferStart + Offset
        if Width == 4:
            Value = struct.unpack_from("<i", Data, ValueOffset)[0]
        elif Width == 8:
            Value = struct.unpack_from("<d", Data, ValueOffset)[0]
        elif Width % 2 == 0:
            Value = _ReadOptimizationCacheText(Data[ValueOffset : ValueOffset + Width], 0)
        else:
            Value = Data[ValueOffset : ValueOffset + Width].hex()
        Inputs[Name] = Value
    return Inputs


def _ParseOptimizationCachePasses(Data: bytes, Offset: int, InitialDeposit: int):
    # Decode the 344-byte result records emitted by the current MetaTrader build.
    if len(Data) % OPT_CACHE_RESULT_SIZE:
        return []
    Fields = (
        "withdrawal",
        "net_profit",
        "gross_profit",
        "gross_loss",
        "maximum_profit_trade",
        "maximum_loss_trade",
        "consecutive_wins_profit",
        "consecutive_losses_loss",
        "maximum_consecutive_profit",
        "maximum_consecutive_loss",
        "minimum_balance",
        "balance_drawdown",
        "balance_drawdown_percent",
        "equity_drawdown",
        "equity_drawdown_percent",
        "minimum_equity",
        "minimum_equity_drawdown",
        "minimum_equity_drawdown_percent",
        "maximum_equity_drawdown",
        "maximum_equity_drawdown_percent",
        "expected_payoff",
        "profit_factor",
        "recovery_factor",
        "sharpe_ratio",
        "minimum_margin_level",
    )
    Passes = []
    for Index in range(0, len(Data), OPT_CACHE_RESULT_SIZE):
        Values = [Value[0] for Value in struct.iter_unpack("<d", Data[Index : Index + OPT_CACHE_RESULT_SIZE])]
        Metrics = dict(zip(Fields, Values[2:27]))
        # MetaTrader derives its Total Trades column from net profit and expected payoff.
        TotalTrades = round(Metrics["net_profit"] / Metrics["expected_payoff"]) if Metrics["expected_payoff"] else 0
        Passes.append(
            {
                "pass": Index // OPT_CACHE_RESULT_SIZE + 1,
                "offset": Offset + Index,
                "symbol": _ReadOptimizationCacheText(Data, Index + 280),
                "initial_deposit": InitialDeposit,
                "criterion": Values[1],
                **Metrics,
                "total_trades": TotalTrades,
            }
        )
    return Passes


def _ParseOptimizationCacheSymbolPasses(Data: bytes, Offset: int, Inputs: dict, Descriptors: list[dict]):
    # Decode standard single-symbol records after their 16-byte cache preamble.
    Fields = (
        "withdrawal",
        "net_profit",
        "gross_profit",
        "gross_loss",
        "maximum_profit_trade",
        "maximum_loss_trade",
        "consecutive_wins_profit",
        "consecutive_losses_loss",
        "maximum_consecutive_profit",
        "maximum_consecutive_loss",
        "minimum_balance",
        "balance_drawdown",
        "balance_drawdown_percent",
        "equity_drawdown",
        "equity_drawdown_percent",
        "minimum_equity",
        "minimum_equity_drawdown",
        "minimum_equity_drawdown_percent",
        "maximum_equity_drawdown",
        "maximum_equity_drawdown_percent",
        "expected_payoff",
        "profit_factor",
        "recovery_factor",
        "sharpe_ratio",
        "minimum_margin_level",
    )
    RecordSize = 296
    FirstRecord = 16
    RequiredSize = 26 * 8
    OptimizedDescriptors = [Descriptor for Descriptor in Descriptors if Descriptor["optimized"]]
    Passes = []
    for Index in range(FirstRecord, len(Data), RecordSize):
        if len(Data) - Index < RequiredSize:
            break
        Values = [Value[0] for Value in struct.iter_unpack("<d", Data[Index : Index + RequiredSize])]
        Metrics = dict(zip(Fields, Values[1:]))
        # MetaTrader derives its Total Trades column from net profit and expected payoff.
        TotalTrades = round(Metrics["net_profit"] / Metrics["expected_payoff"]) if Metrics["expected_payoff"] else 0
        # Decode only values that vary for this optimization pass.
        Parameters = {}
        for ParameterIndex, Descriptor in enumerate(OptimizedDescriptors):
            ValueOffset = Index + 272 + ParameterIndex * 8
            if ValueOffset + 8 > len(Data):
                break
            Name = Descriptor["name"]
            Value = struct.unpack_from("<d", Data, ValueOffset)[0] if isinstance(Inputs.get(Name), float) else struct.unpack_from("<q", Data, ValueOffset)[0]
            Parameters[Name] = Value

        # The final 64-bit field identifies the optimizer's parameter-set ordering.
        SetIndexOffset = Index + 272 + len(OptimizedDescriptors) * 8
        SetIndex = struct.unpack_from("<q", Data, SetIndexOffset)[0] if SetIndexOffset + 8 <= len(Data) else None
        Passes.append(
            {
                "pass": len(Passes) + 1,
                "offset": Offset + Index,
                "initial_deposit": Values[0],
                "parameters": Parameters,
                "parameter_set_index": SetIndex,
                **Metrics,
                "total_trades": TotalTrades,
            }
        )
    return Passes


def ParseOptimizationCache(metaquotes: Path, strategy: str, symbol: str, timeframe: Timeframe):
    # Locate the newest cache that belongs to the requested expert, symbol, and period.
    cache_directory = Path(metaquotes) / "tester" / "cache"
    strategy_name = Path(strategy).stem
    cache_prefix = f"{strategy_name}.{symbol}.{timeframe.value}."
    CacheFiles = sorted(cache_directory.glob(f"{glob.escape(cache_prefix)}*.opt")) if cache_directory.is_dir() else []
    if not CacheFiles:
        Result = {"Optimization": []}
        Result["Error"] = "Cache not found"
        return Result

    # Prefer the newest cache when previous tester runs have left matching artifacts.
    CacheFile = max(CacheFiles, key=lambda File: (File.stat().st_mtime_ns, File.name))
    return ParseOptimizationCacheFile(CacheFile)


def ParseOptimizationCacheFile(cache_file: Path):
    Result = {"Optimization": []}
    try:
        Data = cache_file.read_bytes()
        if len(Data) < 0x54A or _ReadOptimizationCacheText(Data, 0x84) != "TesterOptCache":
            raise ValueError("Not a MetaTrader TesterOptCache file")
        HeaderSize = struct.unpack_from("<I", Data, OPT_CACHE_HEADER_SIZE_OFFSET)[0]
        if not OPT_CACHE_HEADER_SIZE_OFFSET < HeaderSize <= len(Data):
            raise ValueError(f"Invalid TesterOptCache header size {HeaderSize}")

        # Extract fixed metadata, descriptor-backed inputs, and binary pass statistics.
        Header = {
            "format_version": struct.unpack_from("<I", Data, 0)[0],
            "copyright": _ReadOptimizationCacheText(Data, 4),
            "cache_type": _ReadOptimizationCacheText(Data, 0x84),
            "strategy": _ReadOptimizationCacheText(Data, 0x1B4),
            "expert": _ReadOptimizationCacheText(Data, 0x234),
            "server": _ReadOptimizationCacheText(Data, 0x334),
            "symbol": _ReadOptimizationCacheText(Data, 0x3B4),
            "account_mode": _ReadOptimizationCacheText(Data, 0x466),
            "currency": _ReadOptimizationCacheText(Data, 0x506),
            "initial_deposit": struct.unpack_from("<I", Data, 0x546)[0],
        }
        # Select the record layout indicated by all-symbol versus single-symbol cache names.
        Payload = Data[HeaderSize:]
        Descriptors = _GetOptimizationCacheInputDescriptors(Data, HeaderSize)
        Inputs = _ParseOptimizationCacheInputs(Data, HeaderSize, Descriptors)
        Passes = _ParseOptimizationCachePasses(Payload, HeaderSize, Header["initial_deposit"]) if ".all_symbols." in cache_file.name.lower() else _ParseOptimizationCacheSymbolPasses(Payload, HeaderSize, Inputs, Descriptors)
        Result.update({"Header": Header, "Inputs": Inputs, "OptimizedInputs": [Descriptor["name"] for Descriptor in Descriptors if Descriptor["optimized"]], "Optimization": Passes})
    except (OSError, UnicodeError, ValueError, struct.error) as Error:
        Result.update({"Error": str(Error)})
    return Result


def DeployCompiledFile(metaquotes: Path, CompiledPath: str, SubDirectory: str = "", Remove: bool = True):
    # Get the filename from the source path
    filename = os.path.basename(CompiledPath)

    # MQL Subdirectory
    MQLSubdirectory = ""
    type = GetProgramType(CompiledPath)
    if type == "indicator":
        MQLSubdirectory = "Indicators"
    elif type == "expert":
        MQLSubdirectory = "Experts"
    elif type == "script":
        MQLSubdirectory = "Scripts"
    else:
        return None

    # Build destination path safely
    DestinationDir = os.path.join(metaquotes, "MQL5", MQLSubdirectory, SubDirectory)
    Destination = os.path.join(DestinationDir, filename)

    # Create destination directory if needed
    os.makedirs(DestinationDir, exist_ok=True)

    # Copy file (preserves metadata)
    shutil.copy2(CompiledPath, Destination)

    # Optionally remove the original
    if Remove:
        os.remove(CompiledPath)

    return Destination


def _CreateHexFile(expert_path: Path) -> Path:
    # Validate the compiled expert before converting its binary contents.
    expert_path = Path(expert_path)
    if expert_path.suffix.lower() != ".ex5":
        raise ValueError(f"Expected an .ex5 file, received {expert_path}")
    if not expert_path.is_file():
        raise FileNotFoundError(f"Compiled expert not found: {expert_path}")

    # Generate an importable Python module that reconstructs the expert bytes.
    hex_data = expert_path.read_bytes().hex()
    hex_lines = "\n".join(f'    "{hex_data[index:index + 120]}"' for index in range(0, len(hex_data), 120))
    python_path = expert_path.with_name(f"{expert_path.stem}_hex.py")
    python_path.write_text(
        f'"""Embedded hexadecimal data for {expert_path.name}."""\n\n' "EXPERT_BYTES = bytes.fromhex(\n" f"{hex_lines}\n" ")\n",
        encoding="ascii",
    )
    return python_path
