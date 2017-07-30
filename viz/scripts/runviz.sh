DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${DIR}/../
python ${DIR}/closest_over_time_with_anns.py $*
python ${DIR}/closest_over_time_with_shading.py $*
